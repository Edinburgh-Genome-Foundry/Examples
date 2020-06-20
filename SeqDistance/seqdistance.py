import os
import csv
import numpy as np


def make_dict_lowercase(dictionary):
    """Make dictionary lowercase"""
    lowercase_dict = {
        k.lower(): set(l.lower() for l in v) for k, v in dictionary.items()
    }
    return lowercase_dict


def make_dict_uppercase(dictionary):
    """Make dictionary uppercase"""
    uppercase_dict = {
        k.upper(): set(l.upper() for l in v) for k, v in dictionary.items()
    }
    return uppercase_dict


def make_dict_both_case(dictionary):
    """Make dictionary contain letters of both cases"""
    combined_case_dict = {
        k.lower(): set(l.lower() for l in v) | set(l.upper() for l in v)
        for k, v in dictionary.items()
    }
    both_case_dict = combined_case_dict.copy()
    for key, value in combined_case_dict.items():
        both_case_dict[key.upper()] = value
    return both_case_dict


def make_penalty_table(letter_to_letter_matches):
    substitute_costs = np.ones((128, 128), dtype=np.float64)  # 2D array of 1s
    for key, v in letter_to_letter_matches.items():
        for letter in v:
            substitute_costs[ord(key), ord(letter)] = 0
            # the symmetric case is set in another iteration of the loop

    return substitute_costs


def make_letter_to_letter_matches(code_to_nt):
    letter_to_letter_matches = {}
    for code, matches in code_to_nt.items():
        letter_to_letter_matches[code] = set(code)
        for key, value in code_to_nt.items():
            if value & matches != set():
                letter_to_letter_matches[code] = letter_to_letter_matches[code] | set(
                    key
                )

    return letter_to_letter_matches


def hamming(seq, ref, substitute_costs=None, verbose=False):
    """Calculate Hamming distance

    Parameters
    ----------

    seq
      string
    
    ref
      string
    
    substitute_costs
      numpy array (128*128) of substitution costs. The indexes are the ord() values of 
      the first 128 ASCII characters. Note that self-substitution can also be assigned 
      a cost.
    
    verbose
      If True, print alignment.
    """
    if len(seq) != len(ref):
        raise ValueError("seq and ref must have same length!")

    if substitute_costs is None:
        substitute_costs = np.ones((128, 128), dtype=np.float64)
        np.fill_diagonal(substitute_costs, 0)  # self-matches

    distance = 0
    for i, letter in enumerate(seq):
        distance += substitute_costs[ord(letter), ord(ref[i])]

    if verbose:
        print(seq)
        alignment = ""
        for i, letter in enumerate(seq):
            match = "|" if substitute_costs[ord(letter), ord(ref[i])] == 0 else " "
            alignment += match
        print(alignment)
        print(ref)

    return distance


def get_substitute_costs_from_csv(filepath, scale=True):
    """Make penalty table from csv file
    
    Parameters
    ----------
    
    filepath
      Path to csv file. Rows: original letter. Columns: replacement letters.
      Format: 
      ,A,R,N ...
      A,13,3,4
      R,6,17,4
      N,9,4,6
      ...
      The higher the score, the more similar the characters are.

    scale
      If True, do max-min scaling to 0-1, so that highest score has 0 penalty value.
    """
    with open(filepath) as f:
        ncols = len(f.readline().split(","))
    matrix = np.loadtxt(filepath, delimiter=",", usecols=range(1, ncols), skiprows=1)
    if not matrix.shape[0] == matrix.shape[1]:
        raise ValueError("Input is not square matrix")

    if scale:
        matrix -= matrix.min()
        matrix /= matrix.ptp()  # min-max normalization
        matrix = 1 - matrix  # reverse so that highest score has 0 penalty


    with open(filepath, newline="") as f:
        reader = csv.reader(f)
        row1 = next(reader)
    row1.pop(0)

    substitute_costs = np.ones((128, 128), dtype=np.float64)

    for i, from_letter in enumerate(row1):  # row (from)
        for j, to_letter in enumerate(row1):  # column (to)
            substitute_costs[ord(from_letter), ord(to_letter)] = matrix[i, j]

    return substitute_costs


def count_matches(seq_matches, ref_matches, substitute_costs):
    matches = 0
    for s in seq_matches:
        for r in ref_matches:
            if s == r:
                matches += 1
    return matches


def count_substitution_cost(seq_matches, ref_matches, substitute_costs):
    substitution_cost = 0
    for s in seq_matches:
        for r in ref_matches:
            substitution_cost += substitute_costs[ord(r), ord(s)]
    return substitution_cost


def get_uncertainty_costs(ambiguity_code_to_nt_set, substitute_costs=None):
    """Calculate substitution matrix where extended letters encode uncertainty
    
    Parameters
    ----------
    
    ambiguity_code_to_nt_set
      dict of extended letter: {matches}. All letters must be uppercase. 
      (Use make_dict_uppercase())

    substitute_costs
        numpy array of substitute costs between the standard letters. Defaults to 1.
    """
    if substitute_costs is None:
        substitute_costs = np.ones((128, 128), dtype=np.float64)
        np.fill_diagonal(substitute_costs, 0)  # self-matches

    uncertainty_substitute_costs = np.ones((128, 128), dtype=np.float64)

    for seq_letter, seq_matches in ambiguity_code_to_nt_set.items():
        for ref_letter, ref_matches in ambiguity_code_to_nt_set.items():
            len_seq_letter = len(seq_matches)
            len_ref_letter = len(ref_matches)
            cases = len_seq_letter * len_ref_letter
            substitution_cost = count_substitution_cost(
                seq_matches, ref_matches, substitute_costs
            )
            scaled_penalty = substitution_cost / cases
            uncertainty_substitute_costs[
                ord(ref_letter), ord(seq_letter)
            ] = scaled_penalty
            uncertainty_substitute_costs[
                ord(seq_letter), ord(ref_letter)
            ] = scaled_penalty  # symmetric case

    # modify table for upper-lower; lower-upper; lower-lower case matches
    for key in ambiguity_code_to_nt_set.keys():
        for key_ref in ambiguity_code_to_nt_set.keys():
            # upper-lower
            uncertainty_substitute_costs[
                ord(key_ref), ord(key.lower())
            ] = uncertainty_substitute_costs[ord(key_ref), ord(key)]

            # symmetric case
            uncertainty_substitute_costs[
                ord(key.lower()), ord(key_ref)
            ] = uncertainty_substitute_costs[ord(key_ref), ord(key)]

            # lower-upper
            uncertainty_substitute_costs[
                ord(key_ref.lower()), ord(key)
            ] = uncertainty_substitute_costs[ord(key_ref), ord(key)]

            # symmetric case
            uncertainty_substitute_costs[
                ord(key), ord(key_ref.lower())
            ] = uncertainty_substitute_costs[ord(key), ord(key_ref)]

            # lower-lower
            uncertainty_substitute_costs[
                ord(key_ref.lower()), ord(key.lower())
            ] = uncertainty_substitute_costs[ord(key_ref), ord(key)]

            # symmetric case
            uncertainty_substitute_costs[
                ord(key.lower()), ord(key_ref.lower())
            ] = uncertainty_substitute_costs[ord(key), ord(key_ref)]

    return uncertainty_substitute_costs


"""Extended nucleotide letter to nucleotide letter dictionary"""
ambiguity_code_to_nt_set = {
    "A": {"A"},
    "G": {"G"},
    "C": {"C"},
    "T": {"T"},
    "Y": {"C", "T"},
    "R": {"A", "G"},
    "W": {"A", "T"},
    "S": {"G", "C"},
    "K": {"T", "G"},
    "M": {"C", "A"},
    "D": {"A", "G", "T"},
    "V": {"A", "C", "G"},
    "H": {"A", "C", "T"},
    "B": {"C", "G", "T"},
    "X": {"A", "C", "G", "T"},
    "N": {"A", "C", "G", "T"},
}


allowed_aa_transitions = {
    "A": ["G", "A", "V", "L", "I"],
    "B": ["D", "E", "N", "Q", "B", "Z"],
    "C": ["S", "C", "M", "T"],
    "D": ["D", "E", "N", "Q", "B", "Z"],
    "E": ["D", "E", "N", "Q", "B", "Z"],
    "F": ["F", "Y", "W"],
    "G": ["G", "A", "V", "L", "I"],
    "H": ["H", "K", "R"],
    "I": ["G", "A", "V", "L", "I"],
    #     'J': ['J'],
    "K": ["H", "K", "R"],
    "L": ["G", "A", "V", "L", "I"],
    "M": ["S", "C", "M", "T"],
    "N": ["D", "E", "N", "Q", "B", "Z"],
    #     'O': ['O'],
    "P": ["P"],
    "Q": ["D", "E", "N", "Q", "B", "Z"],
    "R": ["H", "K", "R"],
    "S": ["S", "C", "M", "T"],
    "T": ["S", "C", "M", "T"],
    # "U": ['S', 'C', 'U', 'M', 'T'],
    "V": ["G", "A", "V", "L", "I"],
    "W": ["F", "Y", "W"],
    "X": ["X"],
    "Y": ["F", "Y", "W"],
    "Z": ["D", "E", "N", "Q", "B", "Z"],
    ".": ["."],
    "*": ["*"],
}


letter_to_letter_matches_uppercase = make_letter_to_letter_matches(
    ambiguity_code_to_nt_set
)
letter_to_letter_matches = make_dict_both_case(letter_to_letter_matches_uppercase)
nt_substitute_costs = make_penalty_table(letter_to_letter_matches)
aa_substitute_costs = make_penalty_table(allowed_aa_transitions)

uncertainty_substitute_costs = get_uncertainty_costs(
    ambiguity_code_to_nt_set, substitute_costs=None
)
