import re
import Bio
import dnachisel

i_motif = "CCCTTTCCCTTTCCCTTTCCC"
regex = "(CCCTTT){3}C{3}"  # optimal pattern for i-motif formation
query_seq = (
    dnachisel.random_dna_sequence(length=50)
    + i_motif
    + dnachisel.random_dna_sequence(length=50)
)
print(query_seq)
seq = Bio.Seq.Seq(query_seq)

# Find first occurrence:
print(seq.find(i_motif))

# Find all:
matches = [
    (m.start(), m.end()) for m in re.finditer(i_motif, str(seq))
]  # list of tuples
print(seq[matches[0][0] : matches[0][1]])

# Find regex with DNA Chisel:
problem = dnachisel.DnaOptimizationProblem(
    sequence=query_seq, constraints=[dnachisel.AvoidPattern(pattern=regex)]
)
print(problem.constraints_text_summary())


compact_regex = "(C{3}T{3}){3}C{3}"  # variant of the same regex
problem = dnachisel.DnaOptimizationProblem(
    sequence=query_seq, constraints=[dnachisel.AvoidPattern(pattern=compact_regex)]
)
print(problem.constraints_text_summary())
