# Document conversion - Extract figures

In this example we convert a PDF document with Deep Search and exports the figures into PNG files

:point_right: See the [extract_figures.py](./extract_figures.py) example script.


Run the example with

```console
python extract_figures.py -i ../../data/samples/2206.01062.pdf -o results_figures/
```


### Additional dependencies

The PDF to image conversion relies on the `pdftoppm` executable of the Poppler library (GPL license)
https://poppler.freedesktop.org/
The Poppler library can be installed from the most common packaging systems, for example
- On macOS, `brew install poppler`
- On Debian (and Ubuntu), `apt-get install poppler-utils`
- On RHEL, `yum install poppler-utils`
