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
    from weighted_levenshtein import lev

    # Nucleotides
    seq = 'ATGGATCGGCGGGCG' + 'AG' + 'SCtg' + 'ATAAGGTGCTAGCTAAAAAAAAAAAA'
    ref = 'ATGGATCGGCGGGCG' + 'TT' + 'CSTS' + 'ATAAGGTGCTAGCTAAAAAAAAAAAA'  # diff 2

    lev(seq, ref, substitute_costs=seqdistance.nt_substitute_costs)
    # returns 2.0


    # Amino acids
    aa1 = 'HGE'  # tripeptide
    aa2 = 'HGD'

    lev(aa1, aa2, substitute_costs=seqdistance.aa_substitute_costs)
    # returns 0.0


    # The module has an implementation of the Hamming distance too:
    seqdistance.hamming(seq, ref, substitute_costs=seqdistance.nt_substitute_costs, verbose=True)
    # returns 2.0
    # prints:
    # ATGGATCGGCGGGCGAGSCtgATAAGGTGCTAGCTAAAAAAAAAAAA
    # |||||||||||||||  ||||||||||||||||||||||||||||||
    # ATGGATCGGCGGGCGTTCSTSATAAGGTGCTAGCTAAAAAAAAAAAA
