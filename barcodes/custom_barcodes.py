"""CustomBarcodesCollection class for creating DNA barcode sequences."""

# This file is copied and modified from Genedom.BarcodesCollection
# https://github.com/Edinburgh-Genome-Foundry/genedom/blob/71797d580ceba58c3a775e18a863dc5506644174/genedom/BarcodesCollection.py


from collections import OrderedDict
from copy import deepcopy
import os

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.SeqRecord import SeqRecord

from dnachisel import (
    DnaOptimizationProblem,
    EnzymeSitePattern,
    EnforceGCContent,
    AvoidPattern,
    random_dna_sequence,
    RepeatedKmerPattern,
    UniquifyAllKmers,
)


def sequence_to_record(sequence, features=()):
    seq = Seq(sequence)
    seqrecord = SeqRecord(seq, features=list(features))
    seqrecord.annotations["molecule_type"] = "DNA"

    return seqrecord


def annotate_record(
    seqrecord, location="full", feature_type="feature", margin=0, **qualifiers
):
    """Add a feature to a Biopython SeqRecord.


    **Parameters**

    **seqrecord**
    > The Biopython seqrecord to be annotated.

    **location**
    > Either (start, end) or (start, end, strand). (strand defaults to +1)

    **feature_type**
    > The type associated with the feature.

    **margin**
    > Number of extra bases added on each side of the given location.

    **qualifiers**
    > Dictionary that will be the Biopython feature's `qualifiers` attribute.
    """

    if location == "full":
        location = (margin, len(seqrecord) - margin)

    strand = location[2] if len(location) == 3 else 1
    seqrecord.features.append(
        SeqFeature(
            FeatureLocation(location[0], location[1], strand),
            qualifiers=qualifiers,
            type=feature_type,
        )
    )


def write_record(record, target, fmt="genbank"):
    """Write a record as Genbank, FASTA, etc. via Biopython, with fixes."""
    record = deepcopy(record)
    record.name = record.name[:20]
    record.annotations["molecule_type"] = "DNA"
    if hasattr(target, "open"):
        target = target.open("w")
    SeqIO.write(record, target, fmt)


class CustomBarcodesCollection(OrderedDict):
    """Class representing a set of named barcode sequences.

    The constructor takes a list [(name, barcode), ...] as an input.

    Use ``CustomBarcodesCollection.from_specs(n_barcodes=25)`` to generate an
    instance with 25 compatible barcodes.
    """

    def __init__(self, barcodes):
        OrderedDict.__init__(self, barcodes)

    @staticmethod
    def from_specs(
        n_barcodes=384,
        barcode_length=20,
        spacer="",
        forbidden_enzymes=("BsaI",),
        include_spacers=True,
        names_template="B_%03d",
    ):
        """Return a CustomBarcodesCollection object with compatible barcodes.


        **Parameters**

        **n_barcodes**
        > Number of barcodes to design.

        **barcode_length**
        > Length of each barcode.

        **spacer**
        > Spacer to place between each barcode during the optimization,
          ideally the same spacer that will be used when adding the barcode
          to a part.

        **include_spacers**
        > Whether the spacers should be part of the final sequence of the
          barcodes (they still won't be considered part of the annealing
          primer and won't be used for melting temperature computations).

        **forbidden_enzymes**
        > Name of enzymes whose sites should not be in the barcodes.

        **names_template**
        > The template used to name barcode number "i".
        """
        unit_length = barcode_length + len(spacer)
        seq_len = n_barcodes * unit_length
        units_coordinates = [
            (i, i + unit_length) for i in range(0, seq_len, unit_length)
        ]

        constraints = [
            AvoidPattern(EnzymeSitePattern(enzyme)) for enzyme in forbidden_enzymes
        ]
        constraints += [AvoidPattern(RepeatedKmerPattern(4, 1))]

        for start, end in units_coordinates:
            constraints += [
                UniquifyAllKmers(
                    barcode_length, reference=None, location=(end - len(spacer), end)
                ),
                EnforceGCContent(
                    mini=0.3, maxi=0.7, location=(start, end - len(spacer))
                ),
            ]
        problem = DnaOptimizationProblem(
            sequence=random_dna_sequence(seq_len), constraints=constraints
        )
        problem.logger.ignored_bars.add("location")
        problem.resolve_constraints()

        barcodes = [problem.sequence[start:end] for (start, end) in units_coordinates]
        if not include_spacers:
            barcodes = [b[: -len(spacer)] for b in barcodes]
        names = [(names_template % (i + 1)) for i in range(len(barcodes))]
        return CustomBarcodesCollection(zip(names, barcodes))

    def to_sequences_list(self):
        """Return a list of sequences ["ATTG...", "TTCTGT..."]."""

        return list(self.values())

    def to_fasta(self, path=None):
        """Return (and optionally write) a FASTA string of the barcodes."""

        fasta = "\n\n".join(
            ["> %s\n%s" % (name, barcode) for name, barcode in self.items()]
        )
        if path is not None:
            with open(path, "w+") as f:
                f.write(fasta)
        else:
            return fasta

    def to_records(self, path=None):
        """Return (optionally write) individual Genbanks of the barcodes."""
        records = []
        for (name, barcode) in self.items():
            record = sequence_to_record(barcode)
            record.id = name
            annotate_record(record, label=name)
            records.append(record)
        if path is not None:
            for r in records:
                write_record(r, os.path.join(path, "%s.gb" % r.id))

        return records
