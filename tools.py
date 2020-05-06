import genealloy


def differentiate_sequences(seq):
    """Replace codons with synonymous codons in a sequence (keep translation)"""

    if len(seq) % 3 != 0:
        return "Sequence length must be divisible by 3"

    if set(seq) - {"A", "C", "G", "T"} != set():
        return "The sequence must contain only A,T,G,C"

    seq_codons = genealloy.convert_seq_to_codons(seq)
    seq_aa = [genealloy.codon_to_aa[triplet] for triplet in seq_codons]

    aa_to_codon = {}
    for aa in set(genealloy.codon_to_aa.values()):
        aa_to_codon[aa] = []
    for codon, aa in genealloy.codon_to_aa.items():
        aa_to_codon[aa].append(codon)

    modified_triplets = []
    for i, aa in enumerate(seq_aa):
        replacement = seq_codons[i]
        for triplet in aa_to_codon[aa]:
            if triplet != seq_codons[i]:
                replacement = triplet
                break
        modified_triplets.append(replacement)

    modified_seq = "".join(modified_triplets)

    return modified_seq
