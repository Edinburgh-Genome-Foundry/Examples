import dnachisel


def FlipSeq(left, right, emma):
    """Calculate left and right overhangs for assembly section to be flipped
    and return a modified pandas table of the EMMA standard.

    Parameters
    ----------
    left
      str name of the leftmost (5') part of the assembly section that will be flipped.

    right
      str name of the rightmost (3') part of the assembly section that will be flipped.

    EMMA
      pandas dataframe of the EMMA standard.
    """

    left_overhang = emma.loc[emma.slot_name == left, 'left_overhang'].iloc[0]
    right_overhang = emma.loc[emma.slot_name == right, 'right_overhang'].iloc[0]

    new_left_overhang = dnachisel.biotools.reverse_complement(right_overhang)
    new_right_overhang = dnachisel.biotools.reverse_complement(left_overhang)
    
    emma.loc[emma.slot_name == left, 'left_overhang'] = new_left_overhang
    emma.loc[emma.slot_name == right, 'right_overhang'] = new_right_overhang
    
    return emma
