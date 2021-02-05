import os
import re
import pandas

from Bio.Seq import Seq
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.SeqRecord import SeqRecord

script_dir = os.path.dirname(__file__)
seq_dataset = pandas.read_csv(os.path.join(script_dir, "seq.csv"))


def annotate_record(seqrecord, seq_dataset=seq_dataset):
    sequences = seq_dataset["sequence"].to_list()
    names = seq_dataset["name"].to_list()
    for index, sequence in enumerate(sequences):
        len_sequence = len(sequence)
        name = names[index]
        matches = [m.start() for m in re.finditer(sequence, str(seqrecord.seq))]
        for match in matches:
            seqrecord.features.append(
                SeqFeature(FeatureLocation(match, (match + len_sequence)), type=name)
            )

    return seqrecord
