import plasma


def test_prepare_vessel_from_well():
    try:
        import plateo
        from plateo.containers.plates import Plate96
    except:
        return True
    else:
        plate = Plate96()
        mapping = {
            "ampicillin": "Amp",
            "plasmid_amp": "pAmpR",
            "ampr": "AmpR",
            "TOP10_strain": "TOP10",
        }
        components_quantities = {
            "ampicillin": 1,
            "plasmid_amp": 1,
            "ampr": 1,
            "TOP10_strain": 1,
        }
        plate.well_at_index(1).add_content(components_quantities, volume=1)
        vessel = plasma.prepare_vessel_from_well(
            plate.well_at_index(1), mapping=mapping
        )
        assert len(vessel.strains) == 1
        assert vessel.strains[0].name == "TOP10"
        assert vessel.env["plasmids"][0].name == "pAmpR"
        assert vessel.env["molecules"][0].name == "Amp"
