import dnachisel


class SeqSpace:
    """SeqSpace class
    
    Parameters
    ----------

    space
      DNA Chisel MutationSpace instance of the sequence.

    name
      str name of the sequence

    separator
      separator between segment choices (default `,`)
      
    segment_separator
      separator between segments (default `|`)
    """

    def __init__(self, space, name, separator=",", segment_separator="|"):
        self.space = space
        self.name = name
        self.separator = separator
        self.segment_separator = segment_separator

    def get_string(self):
        choice_list = self.space.choices_list

        sequence = ""
        for choice in choice_list:
            seqs = self.separator.join(choice.variants)
            seqs += self.segment_separator
            sequence += seqs
        return sequence

    def make_filetext(self):
        header = ">" + self.name + "\n"
        sequence = self.get_string()
        return header + sequence + "\n"

    def write_file(self, path=None):
        if path is None:
            path = self.name + ".seqspace"
        filetext = self.make_filetext()
        f = open(path, "wb")
        f.write(filetext.encode("utf8"))
        f.close()


def read_seqspace(path, separator=",", segment_separator="|"):
    """Read seqspace from file
    
    Parameters
    ----------

    path
      str path to file written by `SeqSpace().write_file()`
      
    separator
      separator between segment choices (default `,`)
      
    segment_separator
      separator between segments (default `|`)
    """

    f = open(path, "r", encoding="utf8")
    lines = f.read().splitlines()
    f.close()

    if lines[0][0] != ">":
        raise ValueError("Invalid sequence format")
    name = lines[0][1:]  # remove '>'

    if lines[1][-1] != segment_separator:
        raise ValueError(
            "Invalid sequence format: sequence must end in " + segment_separator
        )
    sequence_list = lines[1].split(segment_separator)
    sequence_list.pop()  # the empty string after last segment_separator

    sequence_counter = 0
    mutation_choices = []

    for seq in sequence_list:
        seqs = seq.split(separator)
        mutationchoice_length = len(seqs[0])
        loc = (sequence_counter, sequence_counter + mutationchoice_length)
        choice = dnachisel.MutationSpace.MutationChoice(loc, seqs)

        mutation_choices += [
            choice
        ] * mutationchoice_length  # one MutationChoice for each letter position
        sequence_counter += mutationchoice_length

    space = dnachisel.MutationSpace.MutationSpace(mutation_choices)

    seq_space = SeqSpace(
        space, name, separator=separator, segment_separator=segment_separator
    )

    return seq_space


def make_aa_to_codon_backtable(codontable):
    """Convert a codontable for use with convert_aa_to_seqspace()

    Returns a codontable (dict) in the format `{'F': ['TTT', 'TTC'], 'L': ['TTA', ...`
    
    Parameters
    ----------

    codontable
      dict of codons in the format `{'TTT': 'F', 'TTC': 'F', 'TTA': 'L', ...`
    """

    aa_list = list(set(codontable.values()))
    backtable = {key: [] for key in aa_list}
    for codon, aa in codontable.items():
        backtable[aa] = backtable[aa] + [codon]

    return backtable


def convert_aa_to_seqspace(aa, backtable, name=None):
    """Create a SeqSpace instance from an amino acid sequence
    
    Parameters
    ----------
    
    aa
      str amino acid sequence

    backtable
      dict of amino acids in the format `{'F': ['TTT', 'TTC'], 'L': ['TTA', ...`

    name
      str name attribute of the returned SeqSpace instance (default: amino acid str)
    """

    if name is None:
        name = aa

    mutation_choices = []
    codon_length = len(backtable[aa[0]][0])  # 3 nt / codon

    for i, aminoacid in enumerate(aa):
        seqs = backtable[aminoacid]
        loc = (i * codon_length, i * codon_length + codon_length)
        choice = dnachisel.MutationSpace.MutationChoice(loc, seqs)

        mutation_choices += [choice] * codon_length

    space = dnachisel.MutationSpace.MutationSpace(mutation_choices)

    seq_space = SeqSpace(space, name)
    return seq_space

