import Bio
import dnachisel


class Methylase:
    """Methylase enzyme class
    
    Parameters
    ----------

    name
      string name of the enzyme

    sequence
      string of extended nucleotide characters

    index_pos
      int index of the methylated base on the positive strand

    index_neg
      int index of the methylated base on the negative strand
    """

    complement_table = {
        "A": "T",
        "G": "C",
        "C": "G",
        "T": "A",
        "Y": "R",
        "R": "Y",
        "W": "W",
        "S": "S",
        "K": "M",
        "M": "K",
        "D": "H",
        "V": "B",
        "H": "D",
        "B": "V",
        "X": "X",
        "N": "N",
    }

    @staticmethod
    def reverse(sequence):
        reverse = sequence[::-1]
        return reverse

    @staticmethod
    def complement(sequence):
        complement_letters = [Methylase.complement_table[letter] for letter in sequence]
        complement = "".join(complement_letters)
        return complement

    @staticmethod
    def reverse_complement(sequence):
        r = Methylase.reverse(sequence)
        rc = Methylase.complement(r)
        return rc

    def __init__(self, name, sequence, index_pos, index_neg):
        self.name = name
        self.sequence = sequence
        self.rc = self.reverse_complement(sequence)
        self.index_pos = index_pos
        self.index_neg = index_neg


EcoKDam = Methylase("EcoKDam", "GATC", 1, 2)
EcoKDcm = Methylase("EcoKDcm", "CCWGG", 1, 3)
EcoBI = Methylase("EcoBI", "TGANNNNNNNNTGCT", 2, 11)
EcoKI = Methylase("EcoKI", "AACNNNNNNGTGC", 1, 10)


methylases = [
    EcoKDam,
    EcoKDcm,
    EcoBI,
    EcoKI,
]


class Methylator:
    """Class for finding methylation sites within a pattern (site) in a sequence.

    Parameters
    ----------

    sequence
      string of ATGC characters

    methylases
      list of Methylase class instances

    site
      string of ATGC characters (restriction enzyme recognition site)
    """

    def __init__(self, sequence, methylases, site):
        """Initialize"""
        self.sequence = sequence
        self.methylases = methylases
        self.site = site

        self.pattern = dnachisel.SequencePattern(site)
        self.regions_seq = self.pattern.find_matches(self.sequence)

        self.site_rc = Methylase.reverse_complement(site)
        self.pattern_rc = dnachisel.SequencePattern(self.site_rc)
        self.regions_rc = self.pattern_rc.find_matches(self.sequence)

        self.regions = self.regions_seq + self.regions_rc

    def find_methylation_sites_in_pattern(self):
        """Run find_one_methylation_site_in_pattern() for each enzyme in methylases"""

        print("Matches against methylase enzyme sites:")
        print()
        for methylase in self.methylases:
            self.find_one_methylation_site_in_pattern(methylase)
            print()

    def find_one_methylation_site_in_pattern(self, methylase):
        """Find overlapping methylation and restriction sites"""

        extended_regions = self.extend_restriction_regions(methylase)

        # For matching against positive strand of methylation pattern:
        expression = dnachisel.DnaNotationPattern.dna_sequence_to_regexpr(
            methylase.sequence
        )
        pattern = dnachisel.SequencePattern(expression)

        # For matching against negative strand of methylation pattern:
        expression_rc = dnachisel.DnaNotationPattern.dna_sequence_to_regexpr(
            methylase.rc
        )
        pattern_rc = dnachisel.SequencePattern(expression_rc)

        print(methylase.name)
        print("=" * len(methylase.name))

        for region in extended_regions:
            region_sequence = self.sequence[region.start : region.end]
            print("Region:", region)
            match_location = pattern.find_matches(region_sequence)
            if len(match_location) != 0:
                print("Match in positive strand: %s" % region_sequence)
            else:
                print("Positive strand: -")

            match_location_rc = pattern_rc.find_matches(region_sequence)
            if len(match_location_rc) != 0:
                print("Match in negative strand: %s" % region_sequence)
            else:
                print("Negative strand: -")
            print()

    def extend_restriction_regions(self, methylase):
        """Modify list of dnachisel.Location of restriction sites to include
        flanking nucleotides around restriction sites
        """

        extended_regions = []
        for region in self.regions:
            region = region.extended(
                methylase.index_neg, left=True, right=False
            )  # extension upstream

            m = len(methylase.sequence) - (methylase.index_pos + 1)
            region = region.extended(
                m, upper_limit=len(self.sequence), left=False, right=True
            )  # extension downstream
            extended_regions.append(region)
        return extended_regions


class Dnd(Methylase):
    pass


Dnd_EcoB7A = Dnd("Dnd_EcoB7A", "GAAC", 0, 3)
Dnd_Sli1326 = Dnd("Dnd_Sli1326", "GGCC", 0, 3)
Dnd_VciFF75 = Dnd("Dnd_VciFF75", "CCA", 0, 2)

dnd = [Dnd_EcoB7A, Dnd_Sli1326, Dnd_VciFF75]
