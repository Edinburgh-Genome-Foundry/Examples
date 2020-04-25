# EpiJinn

**EpiJinn** is a Python module that checks whether recognition sites of prokaryotic DNA *methylase enzymes* overlap with a recognition site of a *restriction enzyme*, in a DNA sequence. Methylation of restriction site nucleotides blocks recognition/restriction and thus DNA assembly.

The module contains the `Methylator` class for storing a sequence, methylation enzymes and a restriction enzyme recognition site. It has a method for finding overlaps, and uses [dnachisel](https://edinburgh-genome-foundry.github.io/DnaChisel/) to find sequence matches.

An example overlap:

    ...ccgcatgaagggcgcgccaggtctcaccctgaattcgcg...
                          ggtctc    : BsaI restriction site
                       CCAGGTCTCACC : Match in positive strand
                       CCWGG        : Dcm methylation site
                        *           : methylated cytosine
                          *         : methylated cytosine (on other strand)
                      
For information on the effect of DNA methylation on each enzyme, see the [Restriction Enzyme Database](http://rebase.neb.com/rebase/rebms.html).


## Usage

    import epijinn
    methylator = epijinn.Methylator(str(sequence), epijinn.methylases, site_BsaI)
    methyl.find_methylation_sites_in_pattern()


## Example

    import epijinn
    import Bio

    sequence = 'ATGTCCCCATGCCTAC' + 'AGCAAATC' + 'CGTCTC' + 'A' + 'GGCCCCCCCCCCCCA'  # seq + EcoBI (+ BsmBI +) EcoBI + seq

    rest_dict = Bio.Restriction.Restriction_Dictionary.rest_dict
    site_BsmBI = rest_dict['BsmBI']['site']

    epijinn.EcoBI.sequence
    # 'TGANNNNNNNNTGCT'
    methylator = epijinn.Methylator(sequence, epijinn.methylases, site_BsmBI)
    methylator.find_methylation_sites_in_pattern()

Result:

    Matches against methylase enzyme sites:

    EcoKDam
    =======
    Region: 22-32(+)
    Positive strand: -
    Negative strand: -


    EcoKDcm
    =======
    Region: 21-33(+)
    Positive strand: -
    Negative strand: -


    EcoBI
    =====
    Region: 13-42(+)
    Positive strand: -
    Match in negative strand: TACAGCAAATCCGTCTCAGGCCCCCCCCC


    EcoKI
    =====
    Region: 14-41(+)
    Positive strand: -
    Negative strand: -
