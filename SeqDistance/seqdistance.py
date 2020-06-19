import numpy as np
import csv


def make_dict_lowercase(dictionary):
    """Make dictionary lowercase"""
    lowercase_dict = {
        k.lower(): set(l.lower() for l in v) for k, v in dictionary.items()
    }
    return lowercase_dict


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


def substitute_costs_from_csv(filepath):
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
    """
    with open(filepath) as f:
        ncols = len(f.readline().split(","))
    matrix = np.loadtxt(filepath, delimiter=",", usecols=range(1, ncols), skiprows=1)
    if not matrix.shape[0] == matrix.shape[1]:
        raise ValueError("Input is not square matrix")

    with open(filepath, newline='') as f:
        reader = csv.reader(f)
        row1 = next(reader)
    row1.pop(0)

    substitute_costs = np.ones((128, 128), dtype=np.float64)

    for i, from_letter in enumerate(row1):  # row (from)
        for j, to_letter in enumerate(row1):  # column (to)
            substitute_costs[ord(from_letter), ord(to_letter)] = matrix[i, j]

    return substitute_costs


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
