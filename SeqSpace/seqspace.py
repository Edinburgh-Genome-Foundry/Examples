import dnachisel


class SeqSpace:
    def __init__(self, space, name, separator=",", choice_separator="|"):
        self.space = space
        self.name = name
        self.separator = separator
        self.choice_separator = choice_separator

    def get_string(self):
        choice_list = self.space.choices_list

        sequence = ""
        for choice in choice_list:
            seqs = self.separator.join(choice.variants)
            seqs += self.choice_separator
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


def read_seqspace(path, separator=",", choice_separator="|"):
    f = open(path, "r", encoding="utf8")
    lines = f.read().splitlines()
    f.close()

    if lines[0][0] != ">":
        raise ValueError("Invalid sequence format")
    name = lines[0][1:]  # remove '>'

    if lines[1][-1] != choice_separator:
        raise ValueError(
            "Invalid sequence format: sequence must end in " + choice_separator
        )
    sequence_list = lines[1].split(choice_separator)
    sequence_list.pop()  # the empty string after last choice_separator

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

    seq_space = SeqSpace(space, name, separator=",", choice_separator="|")

    return seq_space
