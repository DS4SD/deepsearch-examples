# Copyright IBM Inc. All rights reserved.
#
# SPDX-License-Identifier: MIT
#

"""
This script is converting a PDF document with Deep Search and exports the figures into PNG files.

The PDF to image conversion relies on the `pdftoppm` executable of the Poppler library (GPL license)
https://poppler.freedesktop.org/
The Poppler library can be installed from the most common packaging systems, for example
- On macOS, `brew install poppler`
- On Debian (and Ubuntu), `apt-get install poppler-utils`
- On RHEL, `yum install poppler-utils`


$ python scripts/extract_figures.py --help
Usage: extract_figures.py [OPTIONS]

Options:
  -i PATH     Input PDF filename  [required]
  -o PATH     Output directory where figures are saved  [required]
  -p TEXT     Deep Search project key  [default:
              1234567890abcdefghijklmnopqrstvwyz123456]
  -r INTEGER  Resolution for the extracted figures  [default: 72]
  -c PATH     Path to the Deep Search config file. Can be generated with
              `deepsearch login --output PATH`  [default: ds-auth.json]
  --help      Show this message and exit.
"""

import json
import math
from pathlib import Path
from zipfile import ZipFile
from typing import List
from subprocess import check_call, CalledProcessError

import typer
import deepsearch as ds


def crop_pdf_to_image(
    pdf_filename: Path, page: int, bbox: List[int], output_filename: Path, resolution=72
):
    """
    Invoke the pdftoppm executable for cropping the given bounding box from the PDF doucment

    Parameters
    ----------
    pdf_filename : Path
        Input PDF file.
    page : int
        Page number where the bounding box is located.
    bbox : List[int]
        Bounding box to extract, in the format [x0, y0, x1, y1], where the origin is the top-left corner.
    output_filename : Path
        Output filename where the PNG image is saved to.
    resolution : int, Default=72
        Resolution of the extracted image.
    """
    cmd = [
        "pdftoppm",
        "-png",
        "-singlefile",
        "-f",
        str(page),
        "-l",
        str(page),
        "-cropbox",
        "-r",
        str(resolution),
        "-x",
        str(bbox[0]),
        "-y",
        str(bbox[1]),
        "-W",
        str(bbox[2] - bbox[0]),
        "-H",
        str(bbox[3] - bbox[1]),
        str(pdf_filename),
        str(output_filename),
    ]
    try:
        check_call(cmd)
    except CalledProcessError as cpe:
        raise RuntimeError(
            f"PDFTOPPM PROCESSING ERROR. Exited with: {cpe.returncode}"
        ) from cpe


def extract_figures_from_json_doc(
    pdf_filename: Path, document: dict, output_dir: Path, resolution: int
):
    """
    Iterate through the converted document format and extract the figures as PNG files

    Parameters
    ----------
    pdf_filename : Path
        Input PDF file.
    document :
        The converted document from Deep Search.
    bbox : List[int]
        Bounding box to extract, in the format [x0, y0, x1, y1], where the origin is the top-left corner.
    output_dir : Path
        Output directory where all extracted images will be saved.
    resolution : int
        Resolution of the extracted image.
    """

    output_base = output_dir / document["file-info"]["filename"].rstrip(".pdf").rstrip(
        ".PDF"
    )
    page_counters = {}
    # Iterate through all the figures identified in the converted document
    for figure in document.get("figures", []):
        prov = figure["prov"][0]
        page = prov["page"]
        page_counters.setdefault(page, 0)
        page_counters[page] += 1

        # Retrieve the page dimensions, needed for shifting the coordinates of the bounding boxes
        page_dims = next(
            (dims for dims in document["page-dimensions"] if dims["page"] == page), None
        )
        if page_dims is None:
            typer.secho(
                f"Page dimensions for page {page} not defined! Skipping it.",
                fg=typer.colors.YELLOW,
            )
            continue

        # Convert the Deep Search bounding box in the coordinate frame used to extract images.
        # From having the origin in the bottom-left corner, to the top-left corner
        # The bounding box is expanded to the closest integer coordinates, because of the format
        # requirements of the tools used in the extraction.
        bbox = [
            math.floor(prov["bbox"][0]),
            math.floor(page_dims["height"] - prov["bbox"][3]),
            math.ceil(prov["bbox"][2]),
            math.ceil(page_dims["height"] - prov["bbox"][1]),
        ]

        # Extract the bounding box
        output_filename = output_base.with_name(
            f"{output_base.name}_{page}_{page_counters[page]}"
        )
        crop_pdf_to_image(
            pdf_filename, page, bbox, output_filename, resolution=resolution
        )
        typer.secho(f"Figure extracted in {output_filename}.png", fg=typer.colors.GREEN)


def main(
    pdf_filename: Path = typer.Option(..., "-i", help="Input PDF filename"),
    output_dir: Path = typer.Option(
        ..., "-o", help="Output directory where figures are saved"
    ),
    proj_key: str = typer.Option(
        "1234567890abcdefghijklmnopqrstvwyz123456", "-p", help="Deep Search project key"
    ),
    resolution: int = typer.Option(
        72, "-r", help="Resolution for the extracted figures"
    ),
    config_file: Path = typer.Option(
        "ds-auth.json",
        "-c",
        help="Path to the Deep Search config file. Can be generated with `deepsearch login --output PATH`",
    ),
):

    typer.secho(f"Using Deep Search config {config_file}", fg=typer.colors.BLUE)

    # Initialize the Deep Search client from the config file
    config = ds.DeepSearchConfig.parse_file(config_file)
    client = ds.CpsApiClient(config)
    api = ds.CpsApi(client)

    # Launch the docucment conversion and download the results
    documents = ds.convert_documents(
        api=api, proj_key=proj_key, source_path=pdf_filename, progress_bar=True
    )
    documents.download_all(result_dir=output_dir, progress_bar=True)

    # Iterate through the zip files which were downloaded and loop through the content of each zip archive
    for output_file in Path(output_dir).rglob("json*.zip"):
        with ZipFile(output_file) as archive:
            all_files = archive.namelist()
            for name in all_files:
                if name.endswith(".json"):
                    typer.secho(
                        f"Procecssing file {name} in archive {output_file}",
                        fg=typer.colors.BLUE,
                    )
                    document = json.loads(archive.read(name))
                    extract_figures_from_json_doc(
                        pdf_filename, document, output_dir, resolution
                    )


if __name__ == "__main__":
    app = typer.Typer(no_args_is_help=True, add_completion=False)
    app.command()(main)
    app()
