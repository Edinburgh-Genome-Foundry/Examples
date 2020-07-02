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
