import pytest
import plasma


def test_set_temperature():
    vessel = plasma.Vessel()
    vessel.set_temperature(35)
    assert vessel.env["temperature"] == 35

    with pytest.raises(ValueError):
        vessel.set_temperature("abc")


def test_add_molecule():
    vessel = plasma.Vessel()
    vessel.add_molecule(plasma.Amp)
    assert vessel.env["molecules"][0].name == "Amp"


def test_add_plasmid():
    vessel = plasma.Vessel()
    vessel.add_plasmid(plasma.dna["pAmpR"])
    assert vessel.env["plasmids"][0].name == "pAmpR"


def test_add_strain():
    vessel = plasma.Vessel()
    vessel.add_strain(plasma.strains["TOP10"])
    assert vessel.strains[0].name == "TOP10"


def test_print_contents():
    vessel = plasma.Vessel()
    assert vessel.print_contents() == None


def test_transform():
    vessel = plasma.Vessel()
    vessel.add_plasmid(plasma.dna["pAmpR"])
    vessel.add_strain(plasma.strains["TOP10"])
    vessel.transform()
    assert hasattr(vessel, "transformation")
    

def test_print_transformation_results():
    vessel = plasma.Vessel()
    assert (
        vessel.print_transformation_results()
        == "Vessel has not been transformed. Run Vessel.transform()"
    )
    vessel.transform()
    assert vessel.print_transformation_results() == None
