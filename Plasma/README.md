# Plasmid assistant

This section is a guide for **Plasm**id **a**daptation for Golden Gate cloning.

The most important steps for adapting a vector (backbone) are ensuring that there are:
* two sites for a restriction enzyme, flanking the insert segment
* no other sites for the restriction enzyme

Additionally, we can add selection for (i) proper assembly (for example, by including ccdB at the insertion location) and for (ii) presence of plasmid in the bacterium (for example, by using antibiotic resistance). Finally, check that the replicon and the partitioning system in the plasmid suits the strain, compatibility and other requirements.


This section also contains a **Plasm**id **a**ssistant Python module that helps in looking up plasmid or bacterium strain properties. It can also *simulate a transformation outcome* by generating plasmid/bacterium combinations, then lists the interactions between genes and molecules in the system. Simulating the *incubation* outcome (survives/grows/perishes) would require modelling the many cases of gene interactions therefore it is not implemented. In the current version, all entities (gene, molecule, plasmid, bacterium) must have a different name.

Note that in genotype descriptions (e.g. *endA1 glnV44 thi-1 gyrA96 relA1* ...) the presence of a gene means that it has *lost* function; minus sign (-) means inactivating mutations, Greek delta (Δ) before a gene name means that the gene is deleted. For more details, see the [ASM guide](https://mcb.asm.org/content/nomenclature).


## Usage

    import plasma

    vessel = plasma.Vessel()
    vessel.add_molecule(plasma.Amp)
    vessel.add_plasmid(plasma.dna["pAmpR"])
    vessel.add_strain(plasma.strains["TOP10"])

    vessel.print_contents()
    # Temperature: 37
    # Strains:
    #     TOP10
    # Plasmids:
    #     pAmpR
    # Molecules:
    #     Amp

    vessel.transform()
    vessel.print_transformation_results()
    # Temperature: 37
    # Molecules: Amp
    # 
    # TOP10 derivatives:
    # TOP10_variant_0
    # Genome: TOP10_chr
    #          araD139 | Interactions: arabinose
    #          galE15 | Interactions: galactose, two_deoxygalactose
    #          galK16 | Interactions: galactose, two_deoxygalactose
    #          rpsL | Interactions: streptomycin
    #          recA1 
    #          endA1 
    #          Deleted F_genes 
    #          Deleted mcrA 
    #          Deleted mrr 
    #          Deleted hsdRMS 
    #          Deleted mcrBC 
    #          Deleted lacZ | Interactions: IPTG, Xgal, colour
    #          Deleted lacX74 
    #          Deleted nupG 
    #          Deleted leu | Interactions: leucine
    #   Plasmids: -
    # 
    # TOP10_variant_1
    # Genome: TOP10_chr
    #          araD139 | Interactions: arabinose
    #          galE15 | Interactions: galactose, two_deoxygalactose
    #          galK16 | Interactions: galactose, two_deoxygalactose
    #          rpsL | Interactions: streptomycin
    #          recA1 
    #          endA1 
    #          Deleted F_genes 
    #          Deleted mcrA 
    #          Deleted mrr 
    #          Deleted hsdRMS 
    #          Deleted mcrBC 
    #          Deleted lacZ | Interactions: IPTG, Xgal, colour
    #          Deleted lacX74 
    #          Deleted nupG 
    #          Deleted leu | Interactions: leucine
    #   Plasmids/genes:
    #      pAmpR
    #        AmpR | Interactions: Amp



## Plateo

Plasma can be used with [Plateo](https://edinburgh-genome-foundry.github.io/Plateo/) to evaluate outcome of a transformation in a plate well.

    import plateo
    from plateo.containers.plates import Plate96

    # We define a correspondence between Plateo well content and Plasma object names:
    mapping = {"ampicillin": "Amp", "plasmid_amp": "pAmpR", "ampr": "AmpR", "DH5alpha_strain": "DH5alpha"}
    # mapping values should match plasma.STORE.keys()

    # Prepare the plate and its well:
    plate = Plate96()
    components_quantities = {"ampicillin": 1, "plasmid_amp": 1, "ampr": 1, "DH5alpha_strain": 1}
    plate.well_at_index(1).add_content(components_quantities, volume=1)

    vessel = plasma.prepare_vessel_from_well(plate.well_at_index(1), mapping=mapping)
    # AmpR is not of class Molecule, Plasmid or Bacterium.
    vessel.transform()
    vessel.print_transformation_results()
    # Temperature: 37
    # Molecules: Amp
    # 
    # DH5alpha derivatives:
    # DH5alpha_variant_0
    # Genome: DH5alpha_chr
    #          gyrA96 | Interactions: nalidixicacid
    #          endA1 
    #          recA1 
    #          purB20 
    #          Deleted F_genes 
    #          Deleted supE44 
    #          Deleted thi | Interactions: thiamine
    #          Deleted relA 
    #          Deleted deoR 
    #          Deleted nupG 
    #          Deleted hsdR 
    #   Plasmids: -
    # 
    # DH5alpha_variant_1
    # Genome: DH5alpha_chr
    #          gyrA96 | Interactions: nalidixicacid
    #          endA1 
    #          recA1 
    #          purB20 
    #          Deleted F_genes 
    #          Deleted supE44 
    #          Deleted thi | Interactions: thiamine
    #          Deleted relA 
    #          Deleted deoR 
    #          Deleted nupG 
    #          Deleted hsdR 
    #   Plasmids/genes:
    #      pAmpR
    #        AmpR | Interactions: Amp


## Planned features

* Genes and strains used in culturing
* Plasmid recombination
* Phage generation simulation
* Sequence attribute for DNA and for Gene
* Load plasmid from a GenBank file or a BioPython record
* Load objects from CSV or JSON files.


## References

S. Marillonnet, R. Grutzner, *Synthetic DNA assembly using golden gate cloning and the hierarchical modular cloning pipeline.* **Current Protocols in Molecular Biology** (2020) 130, e115.

[AddGene](http://www.addgene.org) (a global, nonprofit repository that was created to help scientists share plasmids): *[Plasmids 101: common lab E. coli strains](https://blog.addgene.org/plasmids-101-common-lab-e-coli-strains)*.

[ASM guide](https://mcb.asm.org/content/nomenclature).

[CGSC](https://cgsc.biology.yale.edu) (Coli Genetic Stock Center at Yale University).

[OpenWetWare](https://openwetware.org) (an effort to promote the sharing of information by the [BioBricks Foundation](https://biobricks.org/)): *[E. coli genotypes](https://openwetware.org/wiki/E._coli_genotypes)*.
