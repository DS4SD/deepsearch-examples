# Deep Search integrations - Argilla.io

In this example we will use the output of the converted document for populating a dataset on
[Argilla](https://argilla.io). This enables the user to annotate text for multiple purposes,
e.g. text classification, named entities recognition, etc as well as train custom models fitting their purposes.


:point_right: Run the [argilla_upload.ipynb](./argilla_upload.ipynb) example.


---

## Setup your environment

### Argilla workspace

In this example we require the connection to a running Argilla instance. The easiest method to setup your own
instance is using the 🤗 Hugging Face Space, as documented on https://huggingface.co/docs/hub/spaces-sdks-docker-argilla or
using any other Argilla deployment methods as listed at https://docs.argilla.io/en/latest/getting_started/installation/deployments/deployments.html.

If you don't have one yet, it is very simple to launch a new HF Space using the button below.

[![Deploy Argilla on Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/deploy-to-spaces-lg.svg)](https://huggingface.co/new-space?template=argilla/argilla-template-space)

Note: the Hugging Face installation is not providing persistent storage. Refer to the [official deployment documentation](https://docs.argilla.io/en/latest/getting_started/installation/deployments/deployments.html) for more details.

When running the notebook, make sure to configure the following ENV variables

```bash
export ARGILLA_API_URL="" # for example https://<USER>-<NAME>.hf.space
export ARGILLA_API_KEY="" # for example "admin.apikey"
```

### Language model

When creating the dataset for annotation, you have to split your input text into NLP token. In this example we use the popular spaCy NLP library for this task. The notebook execution will take care of downloading the model which is selected.


## What's next?

Once your documents are converted and loaded into [Argilla](https://docs.argilla.io/en/latest/index.html) you can leverage
all the capabilities this open-source platform for data-centric NLP.

Visit the <a href="https://docs.argilla.io" rel="nofollow" target="_blank">Argilla documentation</a> to learn about its features and check out the <a href="https://docs.argilla.io/en/latest/guides/guides.html" rel="nofollow" target="_blank">Deep Dive Guides</a> and <a href="https://docs.argilla.io/en/latest/tutorials/tutorials.html" rel="nofollow" target="_blank">Tutorials</a>.
