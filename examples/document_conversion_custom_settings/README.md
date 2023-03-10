# Document conversion - Custom settings

## Convert a document with custom pipeline options

```shell
pip install deepsearch-toolkit
```

```py
host = "https://deepsearch-experience.res.ibm.com"
proj = "1234567890abcdefghijklmnopqrstvwyz123456"

username = "<fill-in-your-username>"    # <-- TODO: fill this
api_key = "<fill-in-your-api-key>"      # <-- TODO: fill this

auth = ds.DeepSearchKeyAuth(username=username, api_key=api_key)
config = ds.DeepSearchConfig(host=host, auth=auth)
client = ds.CpsApiClient(config)
api = ds.CpsApi(client)

## Modify OCR pipeline
cs = ConversionSettings.from_project(api, proj_key=proj)
cs.ocr.enabled = True ## Enable or disable OCR

documents = ds.convert_documents(
    api=api,
    proj_key=proj,
    source_path="<path-to-file>",       # <-- TODO: fill this
    conversion_settings=cs,
    progress_bar=True
)
documents.download_all(result_dir="./converted_docs")
info = documents.generate_report(result_dir="./converted_docs")
print(info)
```

## Complete example


A full example on programmatic document conversion can be found in the [convert_documents_custom.ipynb](./convert_documents_custom.ipynb) notebook.
