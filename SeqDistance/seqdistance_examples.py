import seqdistance
import genealloy
from weighted_levenshtein import lev

def hamming(seq, ref):
    """Calculate shortest Hamming distance between a sequence (seq) and subsets of another sequence (ref)"""
    len_seq = len(seq)
    len_ref = len(ref)
    if len_ref < len_seq:
        raise ValueError('Reference is shorter than query!')

    hamming_result = {"Hamming distance": len_seq, "match_positions": dict()}
    for start in range(0, len_ref - len_seq + 1):
        ref_sub = ref[start:(start+len_seq)]
        hamming = lev(seq, ref_sub, substitute_costs=nt_substitute_costs)
        if hamming < hamming_result["Hamming distance"]:
            hamming_result["Hamming distance"] = hamming
            hamming_result["match_positions"] = {start: ref_sub}
        elif hamming == hamming_result["Hamming distance"]:
            hamming_result["match_positions"][start] = ref_sub
    return hamming_result


letter_to_letter_matches_uppercase = seqdistance.make_letter_to_letter_matches(genealloy.ambiguity_code_to_nt_set)
letter_to_letter_matches = seqdistance.make_dict_both_case(letter_to_letter_matches_uppercase)
nt_substitute_costs = seqdistance.make_penalty_table(letter_to_letter_matches)

seq =       'ATGGATCGGCGGGCG'
ref = 'ggGGGCATGGATCGGCGGGCGAGSCtgATAAGGTGCTAGCTAAAAAAAAAA'

lev(seq, ref, substitute_costs=nt_substitute_costs)
# 36.0
# Hamming distance with positions and sequences:
hamming(seq, ref)
# {'Hamming distance': 0.0, 'match_positions': {6: 'ATGGATCGGCGGGCG'}}
########################################################################################
