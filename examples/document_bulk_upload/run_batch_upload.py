#######################################################################################################################
# Run batch uploads to DeepSearch with URL lists or COS prefixes.
#
# Author: cau@zurich.ibm.com
#
# Example usage:
#
# > python run_batch_upload.py \
#   --input-type S3 \
#   --s3-credentials cos.json \ # A JSON of deepsearch.documents.core.models.S3Coordinates
#   --input-file cos_key_prefixes.txt \ # A plain list of prefixes, which are appended to above S3 credentials
#   --concurrency 5 \
#   --instance ds-internal \ # profile name in deepsearch-toolkit
#   --project-key xxx \
#   --collection-key yyy
#
# > python run_batch_upload.py \
#   --input-type URL \
#   --input-file url_list.txt \ # A plain list of HTTP urls to files
#   --batch-size 6 \
#   --concurrency 5 \
#   --instance ds-internal \ # profile name in deepsearch-toolkit
#   --project-key xxx \
#   --collection-key yyy
#
# Notes:
#  - Not supported on deepsearch-experience
#######################################################################################################################

import argparse
import asyncio
import sys
import logging
import os.path
import signal
import uuid
from copy import deepcopy
from enum import Enum

import deepsearch as ds
from deepsearch.cps.apis import public as sw_client
from deepsearch.cps.apis.public import ApiException
from deepsearch.cps.client.components.data_indices import (
    ElasticProjectDataCollectionSource,
    S3Coordinates,
)


class InputSource(Enum):
    S3 = "S3"
    URL = "URL"

    def __str__(self):
        return self.value


chunk_list = lambda lst, n: [lst[i : i + n] for i in range(0, len(lst), n)]

JOB_ID = str(uuid.uuid4())
TASK_POLL_SLEEP_DURATION = 5
RESUME_FILENAME = f"upload_resume_{JOB_ID}.txt"

# Initialize logging
logging.basicConfig(
    filename=f"upload_report_{JOB_ID}.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


async def upload_for_key_prefix(
    api, coords, s3_credentials, key_prefix, semaphore: asyncio.Semaphore
):
    async with semaphore:  # This will limit the number of concurrent uploads
        try:
            cos_coordinates_sub = deepcopy(s3_credentials)
            cos_coordinates_sub.key_prefix = cos_coordinates_sub.key_prefix + key_prefix

            payload = {"s3_source": {"coordinates": cos_coordinates_sub.dict()}}
            task_id = api.data_indices.upload_file(
                coords=coords,
                body=payload,
            )

            print(
                f"Submitting key_prefix={cos_coordinates_sub.key_prefix} with task_id {task_id}..."
            )

            request_status = await wait_for_task(api, coords, task_id)

            print(f"Report for {key_prefix} with task_id {task_id}: {request_status}")
            return [key_prefix], request_status
        except Exception as e:
            logging.error(
                f"Error uploading files for {key_prefix} with task_id {task_id}: {str(e)}"
            )
            return [key_prefix], None


async def upload_for_urls(api, coords, url_batch, semaphore: asyncio.Semaphore):
    async with semaphore:  # This will limit the number of concurrent uploads
        try:

            payload = {"file_url": url_batch}
            task_id = api.data_indices.upload_file(coords=coords, body=payload)

            print(f"Submitting url batch with task_id {task_id}")

            request_status = await wait_for_task(api, coords, task_id)

            print(f"Report for url_batch of task_id {task_id}: {request_status}")
            return url_batch, request_status
        except Exception as e:
            logging.error(
                f"Error uploading files for url_batch with task_id {task_id}: {str(e)}"
            )
            return url_batch, None


async def wait_for_task(api, coords, task_id):
    while True:
        try:
            sw_api = sw_client.TasksApi(api.client.swagger_client)
            r: sw_client.CpsTask = sw_api.get_project_celery_task(
                proj_key=coords.proj_key, task_id=task_id
            )
        except ApiException as e:
            print(
                f"Requesting status of task_id={task_id} failed with HTTP error {e.status}"
            )

            if e.status >= 500:
                await asyncio.sleep(5)
                continue

        request_status = r.to_dict()
        if request_status["task_status"] in ["SUCCESS", "FAILURE"]:
            # return request_status
            break
        else:
            await asyncio.sleep(TASK_POLL_SLEEP_DURATION)

    return request_status


def save_elements(filename: str, items: list):
    with open(filename, "w") as f:
        f.writelines(items)


def handle_exit_signal(a, b):
    print("Received termination signal. Saving current state...")
    save_elements(RESUME_FILENAME, pending_items)
    print("Current state saved. Exiting...")
    sys.exit(0)  # Exit gracefully


async def main():
    global elements
    global pending_items
    global RESUME_FILENAME

    parser = argparse.ArgumentParser(
        description="Bulk upload files to DeepSearch collection"
    )

    # Add the path argument
    parser.add_argument(
        "--input-type",
        "-t",
        type=InputSource,
        choices=list(InputSource),
        default=InputSource.URL,
    )
    parser.add_argument("--input-file", "-l", required=True)
    parser.add_argument("--s3-credentials", "-s3", required=False, default=None)
    parser.add_argument("--batch-size", "-b", type=int, required=False, default=1)
    parser.add_argument("--concurrency", "-n", type=int, required=False, default=5)
    parser.add_argument("--instance", "-i", required=False, default="ds-internal")
    parser.add_argument("--project-key", "-p", required=True)
    parser.add_argument("--collection-key", "-c", required=True)
    parser.add_argument("--resume-point", "-r", required=False, default=None)

    # Parse the command-line arguments
    args = parser.parse_args()

    if not os.path.exists(args.input_file) and not args.resume_point:
        raise argparse.ArgumentTypeError(
            "input-file does not exist, and no resume-point given. Please provide either."
        )

    if args.resume_point is not None and not os.path.exists(args.resume_point):
        raise argparse.ArgumentTypeError("resume-point file does not exist.")

    if args.input_type == InputSource.S3 and not args.s3_credentials:
        raise argparse.ArgumentTypeError(
            "you must provide s3-credentials with input-type S3."
        )

    if args.input_type == InputSource.S3 and not args.batch_size != 1:
        raise argparse.ArgumentTypeError("Batch size must be 1 when using S3 input.")

    if args.input_type == InputSource.S3 and not args.s3_credentials:
        raise argparse.ArgumentTypeError(
            "you must provide s3-credentials with input-type S3."
        )
    
    save_file = args.resume_point if args.resume_point else args.input_file
    with open(save_file) as f:
        print(f"Reading elements from {save_file}")
        elements = list(f.readlines())

    s3_cred = None
    if args.input_type == InputSource.S3:
        s3_cred = S3Coordinates.parse_file(args.s3_credentials)

    RESUME_FILENAME = RESUME_FILENAME or args.resume_point

    pending_items = elements
    save_elements(RESUME_FILENAME, pending_items)
    print(f"To resume this job later, provide --resume-point {RESUME_FILENAME} to the command line.")

    semaphore = asyncio.Semaphore(args.concurrency)
    signal.signal(signal.SIGTERM, handle_exit_signal)
    signal.signal(signal.SIGINT, handle_exit_signal)

    api = ds.CpsApi.from_env(profile_name=args.instance)
    coords = ElasticProjectDataCollectionSource(
        proj_key=args.project_key, index_key=args.collection_key
    )

    loop = asyncio.get_event_loop()

    if args.input_type == InputSource.S3:
        tasks = [
            loop.create_task(
                upload_for_key_prefix(api, coords, s3_cred, prefix, semaphore)
            )
            for prefix in pending_items
        ]
    elif args.input_type == InputSource.URL:
        tasks = [
            loop.create_task(upload_for_urls(api, coords, url_batch, semaphore))
            for url_batch in chunk_list(pending_items, args.batch_size)
        ]

    total_count = len(elements)
    print(f"Processing {total_count} elements.")

    for future in asyncio.as_completed(tasks):
        result = await future
        elements, report = result

        print(f"Batch completed with result: {report}")

        if report is not None:
            for e in elements:
                pending_items.remove(e)

        print(f"{len(pending_items)} of {total_count} left to complete.")

        save_elements(RESUME_FILENAME, pending_items)

        try:
            api.refresh_token()
        except:
            print("Error while refreshing token")
            pass

    print("Upload process completed.")


if __name__ == "__main__":
    asyncio.run(main())
