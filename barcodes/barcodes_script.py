# Make barcodes using DNA Chisel and a class adopted from Genedom:
# %load_ext autoreload
# %autoreload 2

import custom_barcodes

barcode_collection = custom_barcodes.CustomBarcodesCollection.from_specs(n_barcodes=384)

for label, barcode in barcode_collection.items():
    print(barcode)

# Save raw barcodes:
with open("raw_custom_barcodes.csv", "w") as f:
    for key, barcode in barcode_collection.items():
        f.write("%s,%s\n" % (key, barcode))
