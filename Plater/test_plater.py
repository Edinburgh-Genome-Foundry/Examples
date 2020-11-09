import os
import pytest

import plateo
from plateo.parsers import plate_from_content_spreadsheet
import plater


def test_create_gwl_and_platemap_from_csv(tmpdir):
    filename = "data.csv"

    # Starting well set too high:
    with pytest.raises(ValueError):
        plater.create_gwl_and_platemap_from_csv("test", filename, starting_well=383)

    gwl_and_platemap = plater.create_gwl_and_platemap_from_csv("test", filename)
    assert (
        gwl_and_platemap["gwl"].records_to_string()
        == "A;Source1;;4ti-0960/B on CPAC;1;;50;;;;\nD;Destination;;Echo PP P-05525 raised;1;;50;;;;\nW;\nA;Source1;;4ti-0960/B on CPAC;2;;50;;;;\nD;Destination;;Echo PP P-05525 raised;2;;50;;;;\nW;\nA;Source1;;4ti-0960/B on CPAC;3;;50;;;;\nD;Destination;;Echo PP P-05525 raised;3;;50;;;;\nW;\nA;Source1;;4ti-0960/B on CPAC;4;;50;;;;\nD;Destination;;Echo PP P-05525 raised;4;;50;;;;\nW;\nA;Source1;;4ti-0960/B on CPAC;5;;50;;;;\nD;Destination;;Echo PP P-05525 raised;5;;50;;;;\nW;\nA;Source1;;4ti-0960/B on CPAC;6;;50;;;;\nD;Destination;;Echo PP P-05525 raised;6;;50;;;;\nW;\nA;Source1;;4ti-0960/B on CPAC;7;;50;;;;\nD;Destination;;Echo PP P-05525 raised;7;;50;;;;\nW;\nA;Source1;;4ti-0960/B on CPAC;8;;50;;;;\nD;Destination;;Echo PP P-05525 raised;8;;50;;;;\nW;\nA;Source1;;4ti-0960/B on CPAC;9;;50;;;;\nD;Destination;;Echo PP P-05525 raised;9;;50;;;;\nW;\nA;Source2;;4ti-0960/B on carrier;1;;40;;;;\nD;Destination;;Echo PP P-05525 raised;10;;40;;;;\nW;\nA;Source2;;4ti-0960/B on carrier;2;;40;;;;\nD;Destination;;Echo PP P-05525 raised;11;;40;;;;\nW;\n"
    )

    assert (
        gwl_and_platemap["report"]
        == "The starting destination well position is 1 (A1).\n11 transfers listed in gwl.\n"
    )

    destination_path = os.path.join(str(tmpdir), "dest_plate_for_data_csv.xlsx")
    plateo.exporters.plate_to_content_spreadsheet(
        gwl_and_platemap["plate"], destination_path
    )

    assert (
        gwl_and_platemap["plate"]
        .well_at_index(5, direction="column")
        .content.components_as_string()
        == "p15_part_2"
    )

    # Test with non-empty plate:
    destination_plate = plate_from_content_spreadsheet("example_echo_plate.xlsx")
    gwl_and_platemap = plater.create_gwl_and_platemap_from_csv(
        "test", filename, destination_plate=destination_plate
    )


def test_plates_from_geneart_shipment_layout_sheet():
    geneart_plates = plater.plates_from_geneart_shipment_layout_sheet(
        "geneart_example.xlsx"
    )
    assert (
        geneart_plates[1]
        .well_at_index(10, direction="column")
        .content.components_as_string()
    ) == "p6_efgh"


def test_convert_geneart_shipment_file_to_csv(tmpdir):
    destination_path = os.path.join(str(tmpdir), "geneart_example_transfer.csv")
    geneart_plate_csv = plater.convert_geneart_shipment_file_to_csv(
        "geneart_example.xlsx",
        destination_plate_name="Destination",
        destination_plate_type="Echo PP P-05525 raised",
        destination_plate_size=384,
        destination_csv=destination_path,
    )
    assert geneart_plate_csv.source_well_content[11] == "p5_ABCDE"


def test_make_csv_from_fragment_analyzer_report(tmpdir):
    destination_path = os.path.join(str(tmpdir), "fragment_analyzer_transfer.csv")

    plater.make_csv_from_fragment_analyzer_report(
        filepath="fragment_analyzer.csv",
        destination_plate_name="Destination",
        destination_plate_type="4ti-0960/B raised",
        destination_plate_size=96,
        volume_to_transfer=40,
        destination_csv=destination_path,
        source_plate_name="Source1",
        source_plate_type="4ti-0960/B on CPAC",
        source_plate_size=96,
    )
    fa_gwl_and_platemap = plater.create_gwl_and_platemap_from_csv(
        name="FA_test",
        csv_file=destination_path,
        starting_well=1,  # default
        washing_scheme=None,  # default
    )

    fa_gwl_and_platemap["gwl"].records_to_string()
