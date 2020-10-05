# Dioscuri

Python classes and methods for working with **Gemini WorkList** (`gwl`) files and representing Gemini worklists.

A Gemini worklist file is a text file that contains pipetting instructions for the Tecan Freedom EVO robots. Dioscuri uses the Freedom EVOware v2.3 specification of the gwl format.


**Dioscuri** is a name for Castor and Pollux, the twins who were transformed into the Gemini constellation in Greek mythology.

## Load module

import importlib.util
spec = importlib.util.spec_from_file_location("dioscuri", "/path/to/Examples/Dioscuri/dioscuri.py")
dioscuri = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dioscuri)
