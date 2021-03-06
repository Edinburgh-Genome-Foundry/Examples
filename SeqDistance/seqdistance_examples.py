import seqdistance
import genealloy
from weighted_levenshtein import lev


def find_shortest_hamming(seq, ref, substitute_costs):
    """Calculate shortest Hamming distance between a sequence (seq) and 
    subsets of another sequence (ref)"""
    len_seq = len(seq)
    len_ref = len(ref)
    if len_ref < len_seq:
        raise ValueError("Reference is shorter than query!")

    hamming_result = {"Hamming distance": len_seq, "match_positions": dict()}
    for start in range(0, len_ref - len_seq + 1):
        ref_sub = ref[start : (start + len_seq)]
        hamming = seqdistance.hamming(seq, ref_sub, substitute_costs=substitute_costs)
        if hamming < hamming_result["Hamming distance"]:
            hamming_result["Hamming distance"] = hamming
            hamming_result["match_positions"] = {start: ref_sub}
        elif hamming == hamming_result["Hamming distance"]:
            hamming_result["match_positions"][start] = ref_sub
    return hamming_result


letter_to_letter_matches_uppercase = seqdistance.make_letter_to_letter_matches(
    genealloy.ambiguity_code_to_nt_set
)
letter_to_letter_matches = seqdistance.make_dict_both_case(
    letter_to_letter_matches_uppercase
)
nt_substitute_costs = seqdistance.make_penalty_table(letter_to_letter_matches)

seq =       "ATGGATCGGCGGGCG"
#            |||||||||||  ||
ref = "ggGGGCATGGATCGGCGAACGAGSCtgATAAGGTGCTAGCTAAAAAAAAAA"

lev(seq, ref, substitute_costs=nt_substitute_costs)
# 36.0
# Hamming distance with positions and sequences:
find_shortest_hamming(seq, ref, substitute_costs=nt_substitute_costs)
# {'Hamming distance': 2.0, 'match_positions': {6: 'ATGGATCGGCGAACG'}}
########################################################################################

# Calculate distance for complement sequences
from Examples.EpiJinn import epijinn

seq = "AAAAAAAAAACCC"
ref = "GGGTTTTTTTTTT"
print(lev(seq, ref, substitute_costs=nt_substitute_costs))
# 13.0
seq_rc = epijinn.Methylase.reverse_complement(seq)
print(lev(seq_rc, ref, substitute_costs=nt_substitute_costs))
# 0.0
