# SeqDistance

**SeqDistance** is a Python module that provides substitution matrices (penalty tables) for measuring weighted Levenshtein distances between extended (IUPAC) nucleotide (or amino acid) sequences. The matrices can be used with the [weighted-levenshtein](https://github.com/infoscout/weighted-levenshtein) Python package.

## Background

### Nucleotides

In a sequence, an extended nucleotide letter (for example, S = C or G) can mean one of two things: 
* (1) all encoded values match. Then the substitution score is 0.
* (2) there is uncertainty: for example, in the case of S, it's not known whether the nucleotide is C or G, but it's known that it is not A nor T.

Interpreting letters as in the first case (1) and using a substitution matrix for extended nucleotide letters, the Levenshtein distance between the following sequences is 3 (and not 7), because the extended nucleotide S = C or G, and case is ignored (t = T).

    ATCAGSCtgTAGCAA
    |||  |||| |||||
    ATCTTCSTSGAGCAA


In the second case (2), the Levenshtein distance is 4.5:

    ATCAGSCtgTAGCAA
    |||  ??|? |||||
    ATCTTCSTSGAGCAA

The penalty for each letter-pair is calculated by dividing the sum of penalties of each combination by the total number of possible combinations. The letter S means C or G, so there is 50% chance that it matches C. 100%-50% = 50%, so there is also 50% chance for a non-match, therefore the penalty is 0.5.


### Amino acids

Similarly, one can define a substitution matrix for *conservative amino acid replacements.*
Applying that matrix, the distance in the example below is 0, because Glu (E) is a conservative replacement of Asp (D).

    HGE
    |||
    HGD

The module contains a function to generate a substitution matrix for any scoring table from a csv file.


## Usage

    import seqdistance
    from weighted_levenshtein import lev

    # NUCLEOTIDES
    seq = 'ATGGATCGGCGGGCG' + 'AG' + 'SCtg' + 'ATAAGGTGCTAGCTAAAAAAAAAAAA'
    ref = 'ATGGATCGGCGGGCG' + 'TT' + 'CSTS' + 'ATAAGGTGCTAGCTAAAAAAAAAAAA'  # diff 2

    # (1) Extended letters encode match:
    lev(seq, ref, substitute_costs=seqdistance.nt_substitute_costs)
    # returns 2.0


    # (2) Extended letters encode uncertainty. By default, lev() ignores self-substitute costs, therefore as a workaround, we map letters to another set of letters and update the substitute cost table:
    translation_table = seqdistance.make_translation_table(seq, ref)
    updated_substitute_costs = seqdistance.update_substitute_costs(seqdistance.uncertainty_substitute_costs, translation_table) 
    lev(seq.translate(translation_table), ref, substitute_costs=updated_substitute_costs)
    # returns 3.5
    # ..AGSCtg..
    #     ??|?
    # ..TTCSTS..


    # AMINO ACIDS
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
