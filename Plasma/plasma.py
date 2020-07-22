import copy
import itertools

try:
    import plateo
except ImportError:
    _has_plateo = False
else:
    _has_plateo = True


class Vessel:
    """A container for the cloning experiment."""

    def __init__(self):
        self.env = {"temperature": 37, "molecules": [], "plasmids": []}
        self.strains = []

    def add_molecule(self, molecule):
        if not isinstance(molecule, Molecule):
            raise ValueError("Argument must be class Molecule")
        molecules_in_vessel = [m.name.lower() for m in self.env["molecules"]]
        if molecule.name.lower() in molecules_in_vessel:
            raise ValueError("Molecule '%s' is already in the vessel." % molecule.name)
        self.env["molecules"].append(molecule)

    def set_temperature(self, temperature):
        if not (isinstance(temperature, int) or isinstance(temperature, float)):
            raise ValueError("Argument must be class int or float")
        if self.env["temperature"] != temperature:
            self.env["temperature"] = temperature
        else:
            print("Temperature is already %.2f Celsius" % temperature)

    def add_plasmid(self, plasmid):
        if not isinstance(plasmid, Plasmid):
            raise ValueError("Argument must be class Plasmid")
        plasmids_in_vessel = [p.name.lower() for p in self.env["plasmids"]]
        if plasmid.name.lower() in plasmids_in_vessel:
            raise ValueError("Plasmid '%s' is already in the vessel." % plasmid.name)
        self.env["plasmids"].append(plasmid)

    def add_strain(self, strain):
        if not isinstance(strain, Bacterium):
            raise ValueError("Argument must be class Bacterium")
        strains_in_vessel = [s.name.upper() for s in self.strains]
        if strain.name.upper() in strains_in_vessel:
            raise ValueError("Strain '%s' is already in the vessel." % strain.name)
        self.strains.append(strain)

    def print_contents(self):
        print("Temperature:", self.env["temperature"])

        print("Strains:")
        if len(self.strains) == 0:
            print("    No bacteria present")
        else:
            for strain in self.strains:
                print("    ", strain.name)

        print("Plasmids:")
        if len(self.env["plasmids"]) == 0:
            print("    No plasmids present")
        else:
            for plasmid in self.env["plasmids"]:
                print("    ", plasmid.name)

        print("Molecules:")
        if len(self.env["molecules"]) == 0:
            print("    No molecules present")
        else:
            for molecule in self.env["molecules"]:
                print("    ", molecule.name)

    def transform(self):
        """Make new strains by adding all combinations of environmental and 
        self-plasmids to each strain"""

        transformation = {}
        for bacterium in self.strains:
            transformation[bacterium.name] = {}
            all_plasmids = self.env["plasmids"] + bacterium.plasmids

            plasmid_powerset = itertools.chain.from_iterable(
                itertools.combinations(all_plasmids, r)
                for r in range(len(all_plasmids) + 1)
            )  # from itertools documentation

            default_bacterium = copy.deepcopy(bacterium)
            default_bacterium.plasmids = []

            transformation[bacterium.name]["bacterium_variants"] = []
            for i, combination in enumerate(plasmid_powerset):
                new_variant = copy.deepcopy(default_bacterium)
                new_variant.plasmids = combination
                new_variant.name = bacterium.name + "_variant_" + str(i)
                transformation[bacterium.name]["bacterium_variants"].append(new_variant)

        self.transformation = transformation

    def get_interactions(self, gene):
        if len(gene.interactions) == 0:
            return ""
        else:
            return "| Interactions: " + ", ".join(gene.interactions)

    def print_transformation_results(self):
        if not hasattr(self, "transformation"):
            return "Vessel has not been transformed. Run Vessel.transform()"

        print("Temperature:", self.env["temperature"])
        molecule_names = [m.name for m in self.env["molecules"]]
        print("Molecules:", ", ".join(molecule_names))
        print()

        for original_bacterium, variants_dict in self.transformation.items():
            print(original_bacterium, "derivatives:")

            for variant in variants_dict["bacterium_variants"]:
                print(variant.name)
                print("Genome:", variant.chr.name)
                for gene in variant.chr.genes:
                    print("        ", gene.name, self.get_interactions(gene))
                for gene in variant.chr.deleted:
                    print("         Deleted", gene.name, self.get_interactions(gene))
                    # print("         Deleted", gene.name, "| Interactions:", ", ".join(gene.interactions))
                if len(variant.plasmids) == 0:
                    print("  Plasmids: -")
                else:
                    print("  Plasmids/genes:")

                for p in variant.plasmids:
                    print("    ", p.name)
                    for gene in p.genes:
                        print("      ", gene.name, self.get_interactions(gene))
                    for gene in p.deleted:
                        print(
                            "         Deleted", gene.name, self.get_interactions(gene)
                        )
                print()
            print()
            print()


class Gene:
    """Gene

    Parameters
    ----------

    name
      str
    
    interactions
      list of molecule or gene names the gene interacts with
    
    description
      str
    """

    def __init__(
        self, name, interactions=None, description=None,
    ):
        self.name = name
        if interactions is None:
            self.interactions = []
        else:
            self.interactions = interactions
        self.description = description


class DNA:
    """DNA class. It carries genes."""

    def __init__(self, name, genes=None, deleted=None):
        self.name = name
        if genes is None:
            self.genes = []
        else:
            self.genes = genes
        if deleted is None:
            self.deleted = []
        else:
            self.deleted = deleted

    def add_gene(self, gene):
        if not isinstance(gene, Gene):
            raise ValueError("Argument must be class Gene")
        gene_names = [gene.name.lower() for gene in self.genes]

        if gene.name.lower() not in gene_names:
            self.genes.append(gene)
            deleted_names = [gene.name.lower() for gene in self.deleted]
            if gene.name.lower() in deleted_names:
                i = deleted_names.index(gene.name.lower())
                self.deleted.pop(i)
                print(gene.name, "also removed from deleted gene list")
        else:
            print(gene.name, "is already present")

    def delete_gene(self, gene):
        if not isinstance(gene, Gene):
            raise ValueError("Argument must be class Gene")
        deleted_names = [gene.name.lower() for gene in self.deleted]
        if gene.name.lower() in deleted_names:
            print(gene.name, "has already been deleted")
        else:
            self.deleted.append(gene)
            gene_names = [gene.name.lower() for gene in self.genes]
            if gene.name.lower() in gene_names:
                i = gene_names.index(gene.name.lower())
                self.genes.pop(i)
            else:
                print(gene.name, "was not in", self.name, "and was added to deleted")


class Plasmid(DNA):
    """Plasmid"""

    pass


class Chr(DNA):
    """Genome"""

    pass


class Bacterium:
    """Bacterium"""

    def __init__(self, name, plasmids=None, chr=Chr(name="noname"), description=None):
        self.name = name
        self.chr = chr
        if plasmids is None:
            self.plasmids = []
        else:
            self.plasmids = plasmids
        self.description = description


class Molecule:
    """Molecule"""

    def __init__(self, name, description=None):
        self.name = name
        self.description = description


class Phage:
    pass


def prepare_vessel_from_well(well, mapping=None):
    """Prepare a plasma Vessel from a Plateo Well.

    Parameters
    ----------

    well
      Plateo.Well class
    
    mapping
      dict of Well content name: plasma.STORE name. If None, assumes that content names
      match plasma.STORE names.
    """

    if not _has_plateo:
        return "Function requires the Plateo package."

    vessel = Vessel()

    content_names = list(well.content.to_dict()["quantities"].keys())

    if mapping is None:
        store_names = content_names
    else:
        content_in_mapping = set(content_names) & set(mapping.keys())
        store_names = [mapping[e] for e in content_in_mapping]

    for content in store_names:
        if isinstance(STORE[content], Molecule):
            vessel.add_molecule(STORE[content])
        elif isinstance(STORE[content], Bacterium):
            vessel.add_strain(STORE[content])
        elif isinstance(STORE[content], Plasmid):
            vessel.add_plasmid(STORE[content])
        else:
            print("%s is not of class Molecule, Plasmid or Bacterium." % content)

    return vessel


# GENES
AmpR = Gene(
    name="AmpR", interactions=["Amp"], description="Confers resistance to ampicillin"
)
ccdA = Gene(
    name="ccdA", interactions=["ccdB"], description="Confers resistance to ccdB toxin"
)
ccdB = Gene(name="ccdB", interactions=["ccdA"])
Tn10 = Gene(
    name="Tn10",
    interactions=["tetracycline"],
    description="Confers resistance to tetracycline",
)
mCherry = Gene(
    name="mCherry", interactions=["colour"], description="Confers red colour"
)
metB = Gene(name="metB", interactions=["methionine"])
F_genes = Gene(name="F_genes", description="Fertility factor plasmid genes as one gene")
endA1 = Gene(name="endA1", description="Endonuclease I")
supE44 = Gene(name="supE44", description="Synonymous to glnV")
thi = Gene(
    name="thi", interactions=["thiamine"], description="thi-1: thiamine metabolism"
)
recA1 = Gene(name="recA1", description="DNA repair")
relA = Gene(name="relA")
gyrA = Gene(
    name="gyrA",
    interactions=["nalidixicacid"],
    description="DNA gyrase. Confers resistance to nalidixic acid if deleted or mutated.",
)
gyrA96 = Gene(
    name="gyrA96",
    interactions=["nalidixicacid"],
    description="DNA gyrase. This allele confers resistance to nalidixic acid.",
)
deoR = Gene(name="deoR", description="deoR")
nupG = Gene(name="nupG", description="nupG")
purB20 = Gene(
    name="purB20",
    description="Adenylosuccinate lyase mutation. Slow growth in M9 medium",
)
hsdR = Gene(name="hsdR", description="Endonuclease R, host restriction of foreign DNA")
lacZ = Gene(
    name="lacZ",
    interactions=["IPTG", "Xgal", "colour"],
    description="Confers blue colour if IPTG and Xgal present",
)
galE = Gene(
    name="galE",
    interactions=["galactose", "two_deoxygalactose"],
    description="UDPgalactose 4-epimerase",
)
galE15 = Gene(
    name="galE15",
    interactions=["galactose", "two_deoxygalactose"],
    description="High competence, increased resistance to phage P1 infection, and 2-deoxygalactose resistance",
)
galK16 = Gene(
    name="galK16",
    interactions=["galactose", "two_deoxygalactose"],
    description="Cannot metabolize galactose and is resistant to 2-deoxygalactose",
)

mcrA = Gene(
    name="mcrA",
    description="Mutation eliminating restriction of DNA methylated at the sequence CmCGG (possibly mCG)",
)
mrr = Gene(
    name="mrr",
    description="The mrr gene product restricts adenine methylated sequences at CAG or GAC sites",
)
mcrBC = Gene(
    name="mcrBC", description="The mcrBC genes' products restrict RmC sequences"
)
hsdRMS = Gene(
    name="hsdRMS",
    description="Product restricts DNA which is not protected by adenine methylation at sites AA*C[N6]GTGC or GCA*C[N6]GTT",
)
lacX74 = Gene(name="lacX74")
araD = Gene(
    name="araD",
    description="L-ribulose-phosphate 4-epimerase enzyme for arabinose metabolism",
)
araD139 = Gene(
    name="araD139",
    interactions=["arabinose"],
    description="This mutation of araD blocks arabinose metabolism",
)
leu = Gene(
    name="leu",
    interactions=["leucine"],
    description="Leucine biosynthesis. Mutation/deletion causes leucine auxotrophy.",
)
rpsL = Gene(
    name="rpsL",
    interactions=["streptomycin"],
    description="WT ribosomal protein S12. Sensitive to streptomycin.",
)
rpsL_strR = Gene(
    name="rpsL",
    interactions=["streptomycin"],
    description="Streptomycin resistance. Mutation in ribosomal protein S12.",
)
malB_K_12_lamdaS = Gene(
    name="malB_K_12_lamdaS",
    interactions=["maltose"],
    description="The malB region was transduced in from the K-12 strain W3110. Mal+λS. Mutation in phage lambda receptor protein (maltose channel outer membrane protein, maltoporin).",
)
lon_11 = Gene(
    name="lon_11", description="Mutation in lon (ATP-dependent protease LA).",
)
lambda_DE3 = Gene(
    name="lambda_DE3",
    interactions=[""],
    description="DE3, a λ prophage carrying the T7 RNA polymerase gene under the control of the lacUV5 promoter. λDE3 [lacI lacUV5-T7p07 ind1 sam7 nin5]).",
)
hsdS10 = Gene(
    name="hsdS10",
    description="Mutation in hsdS. EcoKI restriction-modification system. Specificity determinant for HsdM and HsdR.",
)
dcm = Gene(name="dcm", description="DNA cytosine methylase",)
galM = Gene(
    name="galM",
    interactions=["galactose", "two_deoxygalactose"],
    description="UDPgalactose 4-epimerase",
)
galK = Gene(
    name="galK",
    interactions=["galactose", "two_deoxygalactose"],
    description="Galactokinase",
)
galT = Gene(
    name="galT",
    interactions=["galactose", "two_deoxygalactose"],
    description="Galactose-1-phosphate uridylyltransferase",
)
ompT = Gene(
    name="ompT",
    description="outer membrane protein protease VII. Mutation/deletion reduces proteolysis of expressed proteins.",
)


# MOLECULES
Amp = Molecule(name="Amp", description="Ampicillin")
IPTG = Molecule(name="IPTG")
methionine = Molecule(name="methionine")
nalidixicacid = Molecule(name="nalidixicacid", description="Targets gyrase")
tetracycline = Molecule(name="tetracycline")
Xgal = Molecule(name="Xgal")
thiamine = Molecule(name="thiamine")
leucine = Molecule(name="leucine")
arabinose = Molecule(name="arabinose")
streptomycin = Molecule(name="streptomycin")
galactose = Molecule(name="galactose")
two_deoxygalactose = Molecule(name="two_deoxygalactose")
maltose = Molecule(name="maltose")


# DNA
pAmpR = Plasmid(name="pAmpR", genes=[AmpR])
F = Plasmid(name="F", genes=[F_genes])
DH5alpha_chr = Chr(
    name="DH5alpha_chr",
    genes=[gyrA96, endA1, recA1, purB20],
    deleted=[F_genes, supE44, thi, relA, deoR, nupG, hsdR],
)
TOP10_chr = Chr(
    name="TOP10_chr",
    genes=[araD139, galE15, galK16, rpsL_strR, recA1, endA1],
    deleted=[F_genes, mcrA, mrr, hsdRMS, mcrBC, lacZ, lacX74, nupG, leu],
)
BL21_DE3_chr = Chr(
    name="BL21_DE3_chr",
    genes=[lon_11, hsdS10, lambda_DE3, malB_K_12_lamdaS],
    deleted=[F_genes, ompT, galM, galK, galT, galE, dcm],
)


# BACTERIA
TOP10 = Bacterium(name="TOP10", chr=TOP10_chr)
DH5alpha = Bacterium(name="DH5alpha", chr=DH5alpha_chr)
BL21_DE3 = Bacterium(
    name="BL21_DE3",
    chr=BL21_DE3_chr,
    description="E. coli B strain variant. Cured of defective P2-like prophage found in wildtype E.coli B.",
)


# STORE
genes = {
    "AmpR": AmpR,
    "ccdA": ccdA,
    "ccdB": ccdB,
    "deoR": deoR,
    "endA1": endA1,
    "hsdR": hsdR,
    "F_genes": F_genes,
    "gyrA": gyrA,
    "gyrA96": gyrA96,
    "lacZ": lacZ,
    "mCherry": mCherry,
    "metB": metB,
    "nupG": nupG,
    "purB20": purB20,
    "recA1": recA1,
    "relA": relA,
    "supE44": supE44,
    "thi": thi,
    "Tn10": Tn10,
    "galE": galE,
    "galE15": galE15,
    "galK16": galK16,
    "mcrA": mcrA,
    "mrr": mrr,
    "mcrBC": mcrBC,
    "hsdRMS": hsdRMS,
    "lacX74": lacX74,
    "araD": araD,
    "araD139": araD139,
    "leu": leu,
    "rpsL": rpsL,
    "rpsL_strR": rpsL_strR,
    "lon_11": lon_11,
    "hsdS10": hsdS10,
    "malB_K_12_lamdaS": malB_K_12_lamdaS,
    "lambda_DE3": lambda_DE3,
    "ompT": ompT,
    "galM": galM,
    "galK": galK,
    "galT": galT,
    "dcm": dcm,
}
molecules = {
    "Amp": Amp,
    "methionine": methionine,
    "IPTG": IPTG,
    "Xgal": Xgal,
    "nalidixicacid": nalidixicacid,
    "tetracycline": tetracycline,
    "thiamine": thiamine,
    "leucine": leucine,
    "arabinose": arabinose,
    "streptomycin": streptomycin,
    "galactose": galactose,
    "two_deoxygalactose": two_deoxygalactose,
    "maltose": maltose,
}
dna = {
    "pAmpR": pAmpR,
    "F": F,
    "DH5alpha_chr": DH5alpha_chr,
    "TOP10_chr": TOP10_chr,
    "BL21_DE3_chr": BL21_DE3_chr,
}
strains = {"TOP10": TOP10, "DH5alpha": DH5alpha, "BL21_DE3": BL21_DE3}

STORE = {**genes, **molecules, **dna, **strains}
