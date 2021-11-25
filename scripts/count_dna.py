# Count sequences and basepairs in a FASTA
###############################################################################
input_files = [
    "example1.fasta",
    "example2.fasta",
    ]
###############################################################################

import dnacauldron as dc

def summarize_fasta_file(input_file):
    parts = dc.biotools.load_records_from_files(files=[input_file], use_file_names_as_ids=False)
    total_length = 0
    for part in parts:
      total_length += len(part.seq)
    print(input_file)
    print(len(parts), "sequences")
    print(total_length, "bp")
    print()


for input_file in input_files:
    summarize_fasta_file(input_file)
