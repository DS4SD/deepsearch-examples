# Copyright IBM Inc. All rights reserved.
#
# SPDX-License-Identifier: MIT
#

"""
This script is converting a PDF document with Deep Search and exports the tables in CSV files.

$ python extract_tables.py --help
Usage: extract_tables.py [OPTIONS]

Options:
  -i PATH  Input PDF filename  [required]
  -o PATH  Output directory where tables are saved  [required]
  -p TEXT  Deep Search project key  [default:
           1234567890abcdefghijklmnopqrstvwyz123456]
  -c PATH  Path to the Deep Search config file. Can be generated with
           `deepsearch login --output PATH`  [default: ../../ds-auth.json]
  --help   Show this message and exit.


For example, run as
$ python extract_tables.py -i ../../data/samples/2206.00785.pdf -o results_tables/
"""

import json
from pathlib import Path
from zipfile import ZipFile

import deepsearch as ds
import pandas as pd
import typer


def extract_tables_from_json_doc(pdf_filename: Path, document: dict, output_dir: Path):
    """
    Iterate through the converted document format and extract the figures as PNG files

    Parameters
    ----------
    pdf_filename : Path
        Input PDF file.
    document :
        The converted document from Deep Search.
    output_dir : Path
        Output directory where all extracted images will be saved.
    """

    output_base = output_dir / document["file-info"]["filename"].rstrip(".pdf").rstrip(
        ".PDF"
    )
    page_counters = {}
    # Iterate through all the tables identified in the converted document
    for table in document.get("tables", []):
        prov = table["prov"][0]
        page = prov["page"]
        page_counters.setdefault(page, 0)
        page_counters[page] += 1

        # Load the table into a Pandas DataFrame
        table_content = [[cell["text"] for cell in row] for row in table["data"]]
        df = pd.DataFrame(table_content)

        # Save table
        output_filename = output_base.with_name(
            f"{output_base.name}_{page}_{page_counters[page]}.csv"
        )
        df.to_csv(output_filename)

        typer.secho(f"Table extracted in {output_filename}", fg=typer.colors.GREEN)


def main(
    pdf_filename: Path = typer.Option(..., "-i", help="Input PDF filename"),
    output_dir: Path = typer.Option(
        ..., "-o", help="Output directory where tables are saved"
    ),
    proj_key: str = typer.Option(
        "1234567890abcdefghijklmnopqrstvwyz123456", "-p", help="Deep Search project key"
    ),
    config_file: Path = typer.Option(
        "../../ds-auth.json",
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
                    extract_tables_from_json_doc(pdf_filename, document, output_dir)


if __name__ == "__main__":
    app = typer.Typer(no_args_is_help=True, add_completion=False)
    app.command()(main)
    app()
