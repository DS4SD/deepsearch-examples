# Deep Search Examples

![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)
[![Jupyter](https://img.shields.io/static/v1?label=jupyter&message=py&color=orange&logo=jupyter)](https://mybinder.org/v2/gh/DS4SD/deepsearch-examples/main)
[![License MIT](https://img.shields.io/github/license/ds4sd/deepsearch-toolkit)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docs](https://img.shields.io/badge/website-live-brightgreen)](https://ds4sd.github.io/deepsearch-toolkit/)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/DS4SD/deepsearch-examples/main)


In this repository we showcase some common usage of Deep Search
for **Document conversion** as well as **Data and Knowledge exploration**. 


## Quick links

- [Deep Search Toolkit](https://github.com/ds4sd/deepsearch-toolkit)
- [Documentation](https://ds4sd.github.io/deepsearch-toolkit/)


## Examples

> Examples rely on having valid credentials in the file `ds-auth.json`.
> To obtain your credentials, please refer to the documentation page https://ds4sd.github.io/deepsearch-toolkit/getting_started/#authentication.
> The file can also be generated via `deepsearch login --output ds-auth.json`

<details>
  <summary>See example</summary>

```json
{
    "host": "https://deepsearch-experience.res.ibm.com",
    "auth": {
        "username": "FILL ME",
        "api_key": "FILL ME"
    },
    "verify_ssl": true
}
```

</details>


### Document conversion

|    | Name              | Description |
| -- | ----------------- | ----------- |
| 1. | [Convert documents quick start](./examples/document_conversion_quick_start/) | Full example on programmatic document conversion |
| 2. | [Visualize bounding boxes](./examples/document_conversion_visualize_bbox/) | Visualize the bbox of the text elements <br /> <img src="./.readme_resources/visualize_bbox.png" width="300px" /> |
| 3. | [Extract figures from documents](./examples/document_conversion_extract_figures/) | Given a PDF file, extract the figures <br /> <img src=".readme_resources/extract_figures.png" width="300px" /> |
| 4. | [Extract tables](./examples/document_conversion_extract_tables/) | Given a PDF file, extract the tables <br /> <img src=".readme_resources/extract_tables.png" width="300px" /> |


### Data queries

This section will showcase examples which query data processed via Deep Search.

|    | Name              | Description |
| -- | ----------------- | ----------- |
| 1. | [Data query quick start](./examples/data_query_quick_start/) | Example listing data collections, making search in one and more document collections, using source for projection |


### Bring your own

This section will showcase examples for bringing your own documents, csv data, nlp models and more.



## Example dependencies

The examples contained in this catalog depend on the `deepsearch-toolkit` as well as
other modules needed for the showcase demonstrated (e.g. `pandas`, `matplotlib`, `rdkit`, etc).
Please refer to the poetry `pyproject.toml` or  `requirements.txt` for a complete list.

Python dependencies are installed with

```console
pip install -r requirements.txt
```

Additionally, some examples rely on system packages. When this is the case, the README of the individual
example will contain more details on which package is required.
The auxiliary file [apt.txt](./apt.txt) list all such packages for a Debian-bases OS. They can be installed with

```console
xargs sudo apt-get install < apt.txt
```


## License

The `Deep Search Toolkit` codebase is under MIT license.
For individual model usage, please refer to the model licenses found in the original packages.
