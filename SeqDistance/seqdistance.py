import numpy as np


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


def hamming(seq, ref, substitute_costs=None):
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
    """
    if len(seq) != len(ref):
        raise ValueError("seq and ref must have same length!")

    if substitute_costs is None:
        substitute_costs = np.ones((128, 128), dtype=np.float64)
        np.fill_diagonal(substitute_costs, 0)  # self-matches

    distance = 0
    for i, letter in enumerate(seq):
        distance += substitute_costs[ord(letter), ord(ref[i])]

    return distance
