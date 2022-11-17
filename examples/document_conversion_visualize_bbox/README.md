# Document conversion - Visualize bboxes

In this example we will use the output of the converted document and create an image of elements detected on each page.

:point_right: Run the [visualize_bbox.ipynb](./visualize_bbox.ipynb) example.


### Additional dependencies

The PDF to image conversion relies on the `pdftoppm` executable of the Poppler library (GPL license)
https://poppler.freedesktop.org/
The Poppler library can be installed from the most common packaging systems, for example
- On macOS, `brew install poppler`
- On Debian (and Ubuntu), `apt-get install poppler-utils`
- On RHEL, `yum install poppler-utils`
