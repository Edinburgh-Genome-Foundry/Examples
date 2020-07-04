import seqspace

from dnachisel.MutationSpace import MutationSpace, MutationChoice

loc1, seqs1 = (0, 2), ["AT", "TG"]
loc2, seqs2 = (2, 5), ["TTC", "TAA", "GGG"]
loc3, seqs3 = (5, 6), ["T"]
c1 = MutationChoice(loc1, seqs1)
c2 = MutationChoice(loc2, seqs2)
c3 = MutationChoice(loc3, seqs3)
space = MutationSpace([c1, c1, c2, c2, c2, c3])


# SeqSpace class tests:
def test_get_string():
    seq_space = seqspace.SeqSpace(space, "test_seq")
    assert seq_space.get_string() == "AT,TG|TTC,TAA,GGG|T|"


def test_make_filetext():
    seq_space = seqspace.SeqSpace(space, "test_seq")
    assert seq_space.make_filetext() == ">test_seq\nAT,TG|TTC,TAA,GGG|T|\n"


# SeqSpace functions:
def test_make_aa_to_codon_backtable():
    codontable = {
        "TTT": "F",
        "TTC": "F",
        "TTA": "L",
        "TTG": "L",
    }
    backtable = seqspace.make_aa_to_codon_backtable(codontable)
    assert backtable == {"L": ["TTA", "TTG"], "F": ["TTT", "TTC"]}


def test_convert_seq_to_seqspace():
    iupac = "AGCTYRWSKMDVHBXN"
    seq_space = seqspace.convert_seq_to_seqspace(iupac, seqspace.ambiguity_code_to_nt)
    assert (
        seq_space.make_filetext()
        == ">AGCTYRWSKMDVHBXN\nA|G|C|T|C,T|A,G|A,T|G,C|T,G|C,A|A,G,T|A,C,G|A,C,T|C,G,T|A,C,G,T|A,C,G,T|\n"
    )

