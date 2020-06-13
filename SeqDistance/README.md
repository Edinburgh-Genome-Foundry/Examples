# SeqDistance

**SeqDistance** is a Python module that provides substitution matrices (penalty tables) for measuring weighted Levenshtein distances between extended (IUPAC) nucleotide (or amino acid) sequences. The matrices can be used with the [weighted-levenshtein](https://github.com/infoscout/weighted-levenshtein) Python package.

## Background

Using a substitution matrix for extended nucleotide letters, the Levenshtein distance between the following sequences is 3 (and not 7), because the extended nucleotide S = C or G, and case is ignored (t = T).

    ATCAGSCtgTAGCAA
    |||  |||| |||||
    ATCTTCSTSGAGCAA

Similarly, one can define a substitution matrix for *conservative amino acid replacements.*
Applying that matrix, the distance in the example below is 0, because Glu (E) is a conservative replacement of Asp (D).

    HGE
    |||
    HGD

The module will be expanded in the future to use nonzero penalty values for conservative replacements.


## Usage

    import seqdistance
    import genealloy
    from weighted_levenshtein import lev

    # Nucleotides
    letter_to_letter_matches_uppercase = seqdistance.make_letter_to_letter_matches(genealloy.ambiguity_code_to_nt_set)
    # include both lower and upper case:
    letter_to_letter_matches = seqdistance.make_dict_both_case(letter_to_letter_matches_uppercase)
    nt_substitute_costs = seqdistance.make_penalty_table(letter_to_letter_matches)

    seq1 = 'ATGGATCGGCGGGCG' + 'AG' + 'SCtg' + 'ATAAGGTGCTAGCTAAAAAAAAAAAA'
    seq2 = 'ATGGATCGGCGGGCG' + 'TT' + 'CSTS' + 'ATAAGGTGCTAGCTAAAAAAAAAAAA'  # diff 2

    lev(seq1, seq2, substitute_costs=nt_substitute_costs)
    # returns 2.0


    # Amino acids
    aa1 = 'HGE'  # tripeptide
    aa2 = 'HGD'

    aa_substitute_costs = seqdistance.make_penalty_table(genealloy.allowed_aa_transitions)
    lev(aa1, aa2, substitute_costs=aa_substitute_costs)
    # returns 0.0


    # The module has an implementation of the Hamming distance too:
    seqdistance.hamming(seq1, seq2, substitute_costs=nt_substitute_costs)
    # returns 2.0
