# SeqSpace

SeqSpace uses [DNA Chisel](https://github.com/Edinburgh-Genome-Foundry/DnaChisel)'s MutationSpace class to read & write ambiguous nucleotide sequences. In most cases, extended IUPAC letters can be used for ambiguous sequences, but not always. For example, the amino acid cysteine (Cys), can be encoded by `TGT`, `TGC` or by `TGY`, using extended letters (Y = T or C); however, an ambiguous nucleotide sequence of serine (Ser, encoded by TCT, TCC, TCA, TCG, AGT, AGC; TCN, AGY) cannot be written using one letter for each position, because the possible values for the second and third letters depend on the first letter.

The possible sequence variants are represented using segments, each with a set of sequence choices:

    AT|TTC|T
    TG|TAA|A 
      |GGG| 

This example represents 2 * 3 * 2 = 12 sequence variants.


## Usage

We create an ambiguous sequence, then write it into a file:

```python
import seqspace
from dnachisel.MutationSpace import MutationSpace, MutationChoice

loc1, seqs1 = (0, 2), ["AT", "TG"]
loc2, seqs2 = (2, 5), ["TTC", "TAA", "GGG"]
loc3, seqs3 = (5, 6), ["T"]
c1 = MutationChoice(loc1, seqs1)
c2 = MutationChoice(loc2, seqs2)
c3 = MutationChoice(loc3, seqs3)
space = MutationSpace([c1, c1, c2, c2, c2, c3])

# Make SeqSpace instance:
seq_space = seqspace.SeqSpace(space, "test_seq")
print(seq_space.get_string())
# AT,TG|TTC,TAA,GGG|T|

seq_space.write_file("example.seqspace")
# The file contents are:
print(seq_space.make_filetext())
# >test_seq
# AT,TG|TTC,TAA,GGG|T|

# Read .seqspace files:
new_seqspace = seqspace.read_seqspace('example.seqspace')
```

We can convert an amino acid (aa) sequence into a mutation space, using a codontable:

```python
from Bio.Data import CodonTable
codontable = CodonTable.unambiguous_dna_by_name['Standard'].forward_table
# Add STOP codons:
codontable["TAA"] = "*"
codontable["TAG"] = "*"
codontable["TGA"] = "*"

# Create an aa sequence and add stop codon:
aa = ''.join(list(CodonTable.unambiguous_dna_by_name['Standard'].back_table.keys())[:-1]) + '*'
print(aa)
# KNTRSIMQHPLEDAGVYCWF*

backtable = seqspace.make_aa_to_codon_backtable(codontable)

seq_space = seqspace.convert_aa_to_seqspace(aa, backtable, name="Amino_acid_seq")
print(seq_space.get_string())
# AAA,AAG|AAT,AAC|ACT,ACC,ACA,ACG|CGT,CGC,CGA,CGG,AGA,AGG|TCT,TCC,TCA,TCG,AGT,AGC|ATT,ATC,ATA|ATG|CAA,CAG|CAT,CAC|CCT,CCC,CCA,CCG|TTA,TTG,CTT,CTC,CTA,CTG|GAA,GAG|GAT,GAC|GCT,GCC,GCA,GCG|GGT,GGC,GGA,GGG|GTT,GTC,GTA,GTG|TAT,TAC|TGT,TGC|TGG|TTT,TTC|TAA,TAG,TGA|
print(seq_space.name)
# Amino_acid_seq
```

## Fileformat

The first line of the seqspace fileformat starts with '>', followed by the sequence name as in fasta: 

    >test_seq
    AT,TG|TTC,TAA,GGG|T|

The second line contains the sequence. The subsegments are separated by a separator character (`|` by default), and the sequence choices are separated by another character (`,`). The sequence ends with the separator character.

