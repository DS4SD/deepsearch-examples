# Bring Your Own PDFs

In this example we combine the document conversion capabilities of Deep Search with its data query capabilities.
From the Deep Search Workspace, we create a new project data index which can host our own PDF documents.
Once the upload is completed, we will be able to query the documents, similar to the public data which we
explored in the [Data query quick start example](../data_query_quick_start/). 

:point_right: Run the [upload_and_explore_pdfs.ipynb](./upload_and_explore_pdfs.ipynb) notebook.


## Access required

The content of this notebook requires access to Deep Search capabilities which are not
available on the public access system.

[Contact us](https://ds4sd.github.io/#unlimited-access) if you are interested in exploring
this Deep Search capabilities.

### Authentication for the restricted instance

When authenticating to Deep Search, you have to use the host of the restricted instance, for example

```console
deepsearch login --host https://deepsearch-ext-v2-535206b87b82b5365d9d6671fbc19165-0000.us-south.containers.appdomain.cloud/ --output ../../ds-auth.ext-v2.json
```


