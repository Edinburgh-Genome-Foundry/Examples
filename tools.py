import genealloy

try:
    import rapidfuzz
except ImportError:
    _has_rapidfuzz = False
else:
    _has_rapidfuzz = True


def differentiate_sequences(seq, verbose=True):
    """Replace codons with synonymous codons in a sequence (keep translation)"""

    verboseprint = print if verbose else lambda *a, **k: None

    if len(seq) % 3 != 0:
        return "Sequence length must be divisible by 3"

    if set(seq) - {"A", "C", "G", "T"} != set():
        return "The sequence must contain only A,T,G,C"

    seq_codons = genealloy.convert_seq_to_codons(seq)
    seq_aa = [genealloy.codon_to_aa[triplet] for triplet in seq_codons]

    verboseprint("The aa sequence is:", "".join(seq_aa))

    aa_to_codon = generate_aa_to_codon(genealloy.codon_to_aa)

    modified_triplets = []
    for i, aa in enumerate(seq_aa):
        replacement = seq_codons[i]
        for triplet in aa_to_codon[aa]:
            if triplet != seq_codons[i]:
                replacement = triplet
                break
        modified_triplets.append(replacement)

    modified_seq = "".join(modified_triplets)

    if _has_rapidfuzz:
        verboseprint(
            "Levenshtein distance of old and new sequence:",
            rapidfuzz.levenshtein.distance(seq, modified_seq),
        )
    else:
        verboseprint("Levenshtein distance requires the rapidfuzz package")

    return modified_seq


def generate_aa_to_codon(codon_to_aa):
    aa_to_codon = {}

    for aa in set(codon_to_aa.values()):
        aa_to_codon[aa] = []
    for codon, aa in codon_to_aa.items():
        aa_to_codon[aa].append(codon)

    return aa_to_codon


def find_best_match(seq, ref):
    """Find alignment with smallest Levenshtein distance between seq and ref.
    Return a dictionary of distances and positions of best matches.

    Parameters
    ----------

    seq
      A string

    ref
      A string, not shorter than seq
    """

    if not _has_rapidfuzz:
        raise ImportError("Function requires the rapidfuzz package.")

    if len(seq) > len(ref):
        raise ValueError("`ref` is shorter than `seq`")

    distances = {}
    for i in range(0, len(ref) - len(seq) + 1):  # moving window of comparison
        distance = rapidfuzz.levenshtein.distance(seq, ref[i : (i + len(seq))])
        distances[(i, i + len(seq))] = distance

    shortest_distance = min(distances.values())

    best_matches = {distance: shortest_distance, "locations": []}
    for location, distance in distances.items():
        if distance == shortest_distance:
            best_matches["locations"].append(location)

    results = {"distances": distances, "best_matches": best_matches}

    return results
