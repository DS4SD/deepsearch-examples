# Export your data

In this example we demonstrate how you can export your data from a given project data
index to JSON. To illustrate this, we first create a demo project and project data index.
Using these resources, we then upload some documents for Deep Search to convert. This
structured data is now easily exported to JSON.

:point_right: Run the [data_export.ipynb](./data_export.ipynb) notebook.

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
