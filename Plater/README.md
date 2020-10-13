# Plater

This module is for generating a Tecan EVO gwl picklist file from a csv file that specifies the transfers. See `data.csv` for the required data and columns.

#### Usage:

```python
import importlib.util
spec = importlib.util.spec_from_file_location("plater", "/path/to/Examples/Plater/plater.py")
plater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(plater)

import plateo
```

---

Generate gwl from csv specifications:

```python
gwl_and_platemap = plater.create_gwl_and_platemap_from_csv(name="test", csv_file="data.csv",
                                                          starting_well=1,  # default
                                                          washing_scheme=None)  # default
gwl_and_platemap.keys()
# dict_keys(['gwl',     # dioscuri.GeminiWorkList()
#            'plate',   # plateo.Plate()
#            'report']) # string of comments
# GeminiWorkList:
gwl_and_platemap["gwl"].records_to_file("picklist.gwl")
# Destination Plate:
plateo.exporters.plate_to_content_spreadsheet(gwl_and_platemap["plate"],
                                              "dest_plate_for_data_csv.xlsx")
# Report on run:
print(gwl_and_platemap["report"])
```

---

Generate gwl from Geneart shipment sheet (edit then use with function above):
```python
geneart_plate_csv = plater.convert_geneart_shipment_file_to_csv(
                                            filepath="geneart_example.xlsx",
                                            destination_plate_name="Destination",
                                            destination_plate_type="Echo PP P-05525 raised",
                                            destination_plate_size=384,
                                            destination_csv="geneart_example_transfer.csv")
# Optional: edit df, then:
geneart_plate_csv.to_csv("transfer.csv", index=False)
```

Generate plate from Geneart shipment sheet (updated version of Plateo's function):
```python
geneart_plates = plater.plates_from_geneart_shipment_layout_sheet("geneart_example.xlsx")
```
This returns a list of plates that can be exported into content spreadsheets as shown above.

---

Transfer clones specified by the [CUBA Analyze Digests](https://cuba.genomefoundry.org/analyze-digests) app:
```python
plate_data = plater.make_csv_from_fragment_analyzer_report(filepath="fragment_analyzer.csv",
                                              destination_plate_name="Destination",
                                              destination_plate_type="4ti-0960/B raised",
                                              destination_plate_size=96,
                                              volume_to_transfer=40,
                                              destination_csv="fragment_analyzer_transfer.csv",
                                              source_plate_name="Source1",
                                              source_plate_type="4ti-0960/B on CPAC",
                                              source_plate_size=96,
                                             )
fa_gwl_and_platemap = plater.create_gwl_and_platemap_from_csv(name="FA_test",
                                                              csv_file="fragment_analyzer_transfer.csv",
                                                              starting_well=1,  # default
                                                              washing_scheme=None  # default
                                                             )
fa_gwl_and_platemap["gwl"].records_to_file("fragment_analyzer_transfer.gwl")
```

