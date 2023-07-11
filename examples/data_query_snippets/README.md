# Data query - Highlighted snippets

When running search queries on large collections, you may be interested in retrieving only
certain details of the query matches, instead of downloading the full documents in the result set.
For instance, you may want to retrieve snippets from some fields where the matches occur or 
you may be interested in just aggregated values from the matched documents. In this example,
we show several search capabilities supported by Deep Search to the make some data anaytics
use cases more efficient.

:point_right: Run the [snippets.ipynb](./snippets.ipynb) notebook.


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


