import genealloy

try:
    import rapidfuzz
except ImportError:
    _has_rapidfuzz = False
else:
    _has_rapidfuzz = True


def differentiate_sequences(seq, ref=None, verbose=True):
    """Replace each codon in a sequence with a synonymous codon that does not match the 
    reference sequence.

    Return a dictionary with a list of possible codons for each position, and also a 
    possible solution.

    Parameters
    ----------

    seq
      A string of ATGC characters, with length divisible by 3.

    ref
      A string of ATGC characters, with same length as seq. If None, use seq. 

    verbose
      Print aa sequence and Levenshtein distances. 
    """

    if ref is None:
        ref = seq

    verboseprint = print if verbose else lambda *a, **k: None

    if len(seq) % 3 != 0:
        raise ValueError("Sequence length must be divisible by 3")

    if len(seq) != len(ref):
        raise ValueError("`seq` and `ref` must be the same length")

    if set(seq + ref) - {"A", "C", "G", "T"} != set():
        raise ValueError("The sequences must contain only A,T,G,C")

    seq_codons = genealloy.convert_seq_to_codons(seq)
    seq_aa = [genealloy.codon_to_aa[triplet] for triplet in seq_codons]

    verboseprint("The aa sequence is:", "".join(seq_aa))

    aa_to_codon = generate_aa_to_codon(genealloy.codon_to_aa)

    modified_seq_codons = []
    for i, triplet in enumerate(seq_codons):
        ref_triplet = ref[i * 3 : i * 3 + 3]
        if triplet != ref_triplet:
            replacement = [triplet]
        else:
            replacement = []
            aa = genealloy.codon_to_aa[triplet]
            for codon in aa_to_codon[aa]:
                if codon != ref_triplet:
                    replacement.append(codon)
            if len(replacement) == 0:
                replacement = [triplet]  # no alternative codon
        modified_seq_codons.append(replacement)

    modified_seq = "".join([codons[0] for codons in modified_seq_codons])

    if _has_rapidfuzz:
        verboseprint(
            "Levenshtein distance (seq vs ref):",
            rapidfuzz.levenshtein.distance(seq, ref),
        )
        verboseprint(
            "Levenshtein distance (modified seq vs ref):",
            rapidfuzz.levenshtein.distance(modified_seq, ref),
        )
    else:
        verboseprint("Levenshtein distance requires the rapidfuzz package")

    return {"solution": modified_seq, "codons": modified_seq_codons}


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
