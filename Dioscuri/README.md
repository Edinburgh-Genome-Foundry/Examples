# Dioscuri

Python classes and methods for working with **Gemini WorkList** (`gwl`) files and representing Gemini worklists.

A Gemini worklist file is a text file that contains pipetting instructions for the Tecan Freedom EVO robots. Dioscuri uses the Freedom EVOware v2.3 specification of the gwl format.


**Dioscuri** is a name for Castor and Pollux, the twins who were transformed into the Gemini constellation in Greek mythology.


## Loading and usage

```python
import importlib.util
spec = importlib.util.spec_from_file_location("dioscuri", "/path/to/Examples/Dioscuri/dioscuri.py")
dioscuri = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dioscuri)


aspirate = dioscuri.Pipette("Aspirate", "Source1", "4ti-0960/B on raised carrier", "3", "50")
aspirate.to_string()

dispense = dioscuri.Pipette("D", "Destination", "4ti-0960/B on CPAC", "1", "50")

wash = dioscuri.WashTipOrReplaceDITI()

worklist = dioscuri.GeminiWorkList(name="my_worklist", records=[aspirate, dispense, wash])
worklist.records_to_string()

print(worklist.records_to_string())
# A;Source1;;4ti-0960/B on raised carrier;3;;50;;;;
# D;Destination;;4ti-0960/B on CPAC;1;;50;;;;
# W;
```
