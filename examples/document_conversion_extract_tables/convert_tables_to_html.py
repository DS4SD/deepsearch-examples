# Copyright IBM Inc. All rights reserved.
#
# SPDX-License-Identifier: MIT
#

"""
This script converts the output of DeepSearch document conversion into a set of HTML tables.

$ python convert_tables_to_html.py --help

 Usage: convert_tables_to_html.py [OPTIONS]

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *                 -i      PATH        Input directory with converted documents (ZIP) [default: None] [required]     │
│ *                 -o      PATH        Output directory where tables are saved [default: None] [required]            │
│    --mode                 [zip|json]  Scan for converted zip files or for document JSON files as input              │
│                                       [default: FileInputMode.zip]                                                  │
│    --struct-only  -s                  Suppress cell content in HTML output                                          │
│    --help                             Show this message and exit.                                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯


For example, run as
$ python convert_tables_to_html.py -i ./converted_docs/ -o ./html/ --mode zip
"""

import json
from enum import Enum
from pathlib import Path
from typing import Annotated
from zipfile import BadZipFile, ZipFile

import typer


class FileInputMode(str, Enum):
    zip = "zip"
    json = "json"


def get_tablecell_span(cell, ix):
    span = set([s[ix] for s in cell["spans"]])
    if len(span) == 0:
        return 1, None, None
    return len(span), min(span), max(span)


def write_table(item, struct_only=False):
    """
    Convert the JSON table representation to HTML, including column and row spans.

    Parameters
    ----------
    item :
        JSON table
    """

    table = item
    body = ""

    nrows = table["#-rows"]
    ncols = table["#-cols"]

    body += "<table>"
    for i in range(nrows):
        body += "<tr>"
        for j in range(ncols):
            cell = table["data"][i][j]

            rowspan, rowstart, rowend = get_tablecell_span(cell, 0)
            colspan, colstart, colend = get_tablecell_span(cell, 1)

            if rowstart is not None and rowstart != i:
                continue
            if colstart is not None and colstart != j:
                continue

            if rowstart is None:
                rowstart = i
            if colstart is None:
                colstart = j

            content = cell["text"].strip()
            # if content == '':
            #    content = '&nbsp;'

            label = cell["type"]
            label_class = "body"
            if label in ["row_header", "row_multi_header", "row_title"]:
                label_class = "header"
            elif label in ["col_header", "col_multi_header"]:
                label_class = "header"

            # celltag = 'th' if label_class == 'header' else 'td'
            celltag = "td"
            style = 'style="text-align: center;"' if label_class == "header" else ""

            opening_tag = f"{celltag}"  # rowstart="{rowstart}" colstart="{colstart}"'
            # if style:
            #    opening_tag += f' {style}'
            if rowspan > 1:
                opening_tag += f' rowspan="{rowspan}"'
            if colspan > 1:
                opening_tag += f' colspan="{colspan}"'

            body += f'<{opening_tag}>{content if not struct_only else ""}</{celltag}>'

        body += "</tr>"

    body += "</table>"

    return body


def wrap_html(tabstr):
    struct_html = (
        """<html>
    <head>
    <meta charset="UTF-8">
    <style>
    table, th, td {
        border: 1px solid black;
        font-size: 10px;
    }
    </style>
    </head>
    <body>
    """
        + tabstr
        + """
    </body>
    </html>"""
    )
    return struct_html


def extract_tables_from_json_doc(
    document: dict, output_dir: Path, structure_only: bool
):
    """
    Iterate through the converted document format and extract the figures as PNG files

    Parameters
    ----------
    document :
        The converted document from Deep Search.
    output_dir : Path
        Output directory where all extracted images will be saved.
    """

    output_base = output_dir / Path(document["file-info"]["filename"]).stem

    page_counters = {}

    # Iterate through all the tables identified in the converted document
    for table in document.get("tables", []):
        prov = table["prov"][0]
        page = prov["page"]
        page_counters.setdefault(page, 0)
        page_counters[page] += 1

        output_filename_html = output_base.with_name(
            f"{output_base.name}_{page}_{page_counters[page]}.html"
        )
        output_filename_html_struct = output_base.with_name(
            f"{output_base.name}_{page}_{page_counters[page]}_structonly.html"
        )

        html_str = write_table(table, struct_only=structure_only)

        with open(output_filename_html, "w") as fp:
            fp.write(wrap_html(html_str))

        typer.secho(f"Table extracted in {output_filename_html}", fg=typer.colors.GREEN)

        yield {
            "filename": document["file-info"]["filename"],
            "full_predicted_table_html": html_str,
            "page_no": page,
            "counter_in_page": page_counters[page],
        }


def main(
    input_dir: Path = typer.Option(
        ..., "-i", help="Input directory with converted documents (ZIP)"
    ),
    output_dir: Path = typer.Option(
        ..., "-o", help="Output directory where tables are saved"
    ),
    mode: Annotated[
        FileInputMode,
        typer.Option(
            case_sensitive=False,
            help="Scan for converted zip files or for document JSON files as input",
        ),
    ] = FileInputMode.zip,
    structure_only: bool = typer.Option(
        False, "--struct-only", "-s", help="Suppress cell content in HTML output"
    ),
):
    with open(output_dir / "table_predictions.jsonl", "w") as fp:

        if mode == FileInputMode.zip:
            bad_zips = 0
            # Iterate through the zip files which were downloaded and loop through the content of each zip archive

            for output_file in Path(input_dir).rglob("json*.zip"):
                typer.secho(f"Processing archive {output_file}")
                try:
                    with ZipFile(output_file) as archive:
                        all_files = archive.namelist()
                        for name in all_files:
                            if name.endswith(".json"):
                                typer.secho(
                                    f"Procecssing file {name} in archive {output_file}",
                                    fg=typer.colors.BLUE,
                                )
                                document = json.loads(archive.read(name))

                                for table_item in extract_tables_from_json_doc(
                                    document, output_dir, structure_only=structure_only
                                ):
                                    fp.write(f"{json.dumps(table_item)}\n")
                except BadZipFile as e:
                    bad_zips += 1

            typer.secho(f"Ignored {bad_zips} bad zip files.")

        elif mode == FileInputMode.json:
            for output_file in Path(input_dir).rglob("*.json"):
                typer.secho(f"Processing file {output_file}", fg=typer.colors.BLUE)
                with open(output_file, "r") as fin:
                    document = json.loads(fin.read())

                    for table_item in extract_tables_from_json_doc(
                        document, output_dir, structure_only=structure_only
                    ):
                        fp.write(f"{json.dumps(table_item)}\n")


if __name__ == "__main__":
    app = typer.Typer(no_args_is_help=True, add_completion=False)
    app.command()(main)
    app()
