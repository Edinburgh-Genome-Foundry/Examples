# SeqFlipper

![alt-text-1](SeqFlipper.png "SeqFlipper")

**SeqFlipper** is a Python module that helps in designing flipped sections of DNA assemblies. This is useful when we already have the DNA parts for the section, but need them in the other direction.

    import seqflipper

The module contains the `FlipSeq()` function that converts the EMMA table file (read as a pandas dataframe) that we use with [genedom](https://edinburgh-genome-foundry.github.io/genedom/index.html).

The method requires that we can define the left overhang of the first part and the right overhang of the last part of the flipped section, therefore it is best practice to flank the section with connectors. For a detailed description, see the [example Jupyter notebook](seqflipper.ipynb)
