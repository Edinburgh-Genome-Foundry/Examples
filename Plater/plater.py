import pandas
import plateo
from plateo.containers import Plate96, Plate384
import dioscuri


def create_gwl_and_platemap_from_csv(
    name,
    csv_file,
    starting_well=1,
    washing_scheme=None,
    destination_plate=None,
    destination_specified=False,
):
    """Generate a `dict` of a dioscuri.GeminiWorkList() and a Plate from a csv file.

    **Parameters**

    **name**
    > Name of the project.

    **csv_file**
    > The csv file containing the transfers. There must be only one destination plate
    > specified. The required csv columns are:
        source_well
        source_well_content  # optional: no plate map generated if any missing.
        source_well_concentration  # nanogram/microliter (ng/uL). Optional.
        source_well_volume  # optional
        source_plate_name
        source_plate_type
        source_plate_size  # only `96` or `384`
        volume_to_transfer  # microliter (uL)
        destination_plate_name  # only one destination plate
        destination_plate_type  # only one destination plate
        destination_plate_size  # only one destination plate (only `96` or `384`)

    > Optional column: 'destination_well'. Set 'destination_specified' True to use it.

    **starting_well**
    > The index of the starting well: skip wells before starting well. Default `1`.

    **washing_scheme**
    > The washing_scheme (1-4) to use between the transfers. Default uses "W;".

    **destination_plate**
    > The destination plate. Default `None` creates a new empty destination plate.

    **destination_specified**
    > `bool`. If True, then use the 'destination_well' column,
    and ignore 'starting_well' parameter.
    """
    if destination_specified:
        print("Destination wells are specified. Ignoring 'starting_well' parameter.")

    report = ""  # this collects various results during run

    df = pandas.read_csv(csv_file)  # read_transfer_table

    if "destination_well" in df.columns and not destination_specified:
        print(
            "'destination_specified' is set to False: ignoring 'destination_well' column."
        )

    # Input checks:
    if not len(set(df.destination_plate_name)) == 1:
        raise ValueError("There must be only one destination plate specified")
    if not len(set(df.destination_plate_size)) == 1:
        raise ValueError("There must be only one destination plate size specified")
    if not len(set(df.destination_plate_type)) == 1:
        raise ValueError("There must be only one destination plate type specified")

    if df.destination_plate_size[0] not in [96, 384]:
        raise ValueError("Only 96-well and 384-well destination plates are supported.")
    if set(df.source_plate_size) - set([96, 384]) != set():
        raise ValueError("Only 96-well and 384-well source plates are supported.")

    if destination_specified:
        # dioscuri.GeminiWorkList:
        gwl = create_worklist_data_object_using_destination_wells(
            name, df, washing_scheme
        )
        report += "%d transfers listed in gwl.\n" % (len(df["destination_well"]))

        try:
            plate = create_destination_plate(name, df, destination_plate)
        except Exception as e:
            print("Cannot create destination plate!")
            print(e)
            plate = None
            report += "\nDestination plate not created.\n"

        return {"gwl": gwl, "plate": plate, "report": report}

    else:  # original workflow

        if (starting_well + len(df.destination_plate_type)) > int(
            df.destination_plate_size[0] + 1
        ):  # add 1 because starting_well is not zero-based
            raise ValueError("Cannot do transfer: starting well value is too big")

        # dioscuri.GeminiWorkList:
        gwl = create_worklist_data_object(name, df, starting_well, washing_scheme)

        destination_well_list = list(
            range(starting_well, (starting_well + len(df.destination_plate_type)))
        )
        print(destination_well_list)
        wellnames = [
            plateo.tools.index_to_wellname(
                index=index, num_wells=df.destination_plate_size[0], direction="column"
            )
            for index in destination_well_list
        ]
        df["destination_well"] = wellnames

        report += "The starting destination well position is %d (%s).\n" % (
            starting_well,
            df["destination_well"][0],
        )
        report += "%d transfers listed in gwl.\n" % (len(df["destination_well"]))

        try:
            plate = create_destination_plate(name, df, destination_plate)
        except Exception as e:
            print("Cannot create destination plate!")
            print(e)
            plate = None
            report += "\nDestination plate not created.\n"

        return {"gwl": gwl, "plate": plate, "report": report}


def create_gwl_record_triplet(entry, current_destination_well, washing_scheme):
    """Generate three gwl records, aspirate, dispense and wash, for a transfer."""
    source_well = entry.source_well
    source_plate_name = entry.source_plate_name
    source_plate_type = entry.source_plate_type
    source_plate_size = int(entry.source_plate_size)
    destination_plate_name = entry.destination_plate_name
    destination_plate_type = entry.destination_plate_type
    # destination_plate_size = entry.destination_plate_size
    volume = entry.volume_to_transfer

    record_triplet = []

    # Generate 3 records
    tecan_well = plateo.tools.wellname_to_index(
        wellname=source_well, num_wells=source_plate_size, direction="column",
    )

    # Aspirate
    aspirate = dioscuri.Pipette(
        "A",
        rack_label=source_plate_name,
        rack_type=source_plate_type,
        position=tecan_well,
        volume=volume,
    )
    record_triplet.append(aspirate)

    # Dispense
    dispense = dioscuri.Pipette(
        "D",
        rack_label=destination_plate_name,
        rack_type=destination_plate_type,
        position=current_destination_well,
        volume=volume,
    )
    record_triplet.append(dispense)

    # Wash
    wash = dioscuri.WashTipOrReplaceDITI(scheme=washing_scheme)
    record_triplet.append(wash)

    return record_triplet


def create_destination_plate(name, df, destination_plate=None):
    if any(pandas.isna(df.source_well_content)):
        raise ValueError("Error: missing content")

    if any(pandas.isna(df.source_well_concentration)):
        raise ValueError("Error: missing concentration")

    if destination_plate is None:
        if df.destination_plate_size[0] == 96:
            plate = Plate96(name=name)
        elif df.destination_plate_size[0] == 384:
            plate = Plate384(name=name)
        else:  # should not occur if called by create_gwl_and_platemap_from_csv()
            raise ValueError(
                "Only 96-well and 384-well destination plates are supported."
            )
    else:
        plate = destination_plate

    for i, row in df.iterrows():
        well = plate.wells[row.destination_well]
        # if not well.is_empty:
        #     raise ValueError(
        #         "Error: destination plate well %s is not empty" % row.destination_well
        #     )
        well.data = {"source_well_content": row.source_well_content}
        volume_microl = row["volume_to_transfer"]  # microliter (uL)
        volume_in_l = volume_microl * 1e-6
        quantity = volume_microl * row["source_well_concentration"] * 1e-9  # ng / uL
        part_label = row.source_well_content
        well.add_content({part_label: quantity}, volume=volume_in_l)

    return plate


def create_worklist_data_object_using_destination_wells(
    name, df, washing_scheme,
):
    """Alternative version for case where destination well is specified."""

    records = []
    destination_plate_size = int(df.destination_plate_size[0])

    for index, row in df.iterrows():
        tecan_destination_well = plateo.tools.wellname_to_index(
            wellname=row.destination_well,
            num_wells=destination_plate_size,
            direction="column",
        )

        gwl_record_triplet = create_gwl_record_triplet(
            row, tecan_destination_well, washing_scheme
        )
        records += gwl_record_triplet

    worklist = dioscuri.GeminiWorkList(name=name, records=records)

    return worklist


def create_worklist_data_object(
    name, df, starting_well, washing_scheme,
):
    """Starting well in Tecan well format."""

    records = []
    current_destination_well = starting_well

    for index in df.index:
        gwl_record_triplet = create_gwl_record_triplet(
            df.iloc[index], current_destination_well, washing_scheme
        )
        records += gwl_record_triplet
        current_destination_well += 1

    worklist = dioscuri.GeminiWorkList(name=name, records=records)

    return worklist


def convert_geneart_shipment_file_to_csv(
    filepath,
    destination_plate_name,
    destination_plate_type,
    destination_plate_size,
    destination_csv=None,
):
    """Create a csv file from a shipment layout sheet and return the corresponding df.

    The csv file can be used with the function `create_gwl_and_platemap_from_csv().`
    Only 96-well source plates are supported.
    """
    source_plate_size = 96  # 96-well plates are shipped

    plates_data = pandas.read_excel(filepath, skiprows=3)  # skip the first 3 rows
    plates_data = plates_data.rename(
        columns={
            "Gene_Name": "source_well_content",
            "Concentration [µg/µl]": "source_well_concentration",
            "Volume [µl]": "source_well_volume",
            "Pos": "source_well",
            "Plate": "source_plate_name",
        }
    )
    # Genart supplies microgram/microliter, we need nanogram/microliter (ng/uL):
    plates_data["source_well_concentration"] *= 1000

    plates_data["source_plate_size"] = source_plate_size
    plates_data["volume_to_transfer"] = "ENTER VOLUME TO TRANSFER (uL)"
    plates_data["source_plate_type"] = "ENTER SOURCE PLATE TYPE"
    plates_data["destination_plate_name"] = destination_plate_name
    plates_data["destination_plate_type"] = destination_plate_type
    plates_data["destination_plate_size"] = destination_plate_size
    if destination_csv is not None:
        plates_data.to_csv(destination_csv, index=False)

    return plates_data


def plates_from_geneart_shipment_layout_sheet(filepath):
    """Return a list of all plates (Plate96) in the shipment layout sheet.

    A layout sheet can contain data for more than one plate, therefore a list of
    Plateo plates are returned, instead of one plate.

    Example
    -------

    >>> plates = plates_from_geneart_shipment_layout_spreadsheet(filepath="2020XYZ.xlsx")
    >>> # Write the plates in plate layout spreadsheet format:
    >>> for plate in plates:
    >>>     plateo.exporters.plate_to_content_spreadsheet(plate, "./%s.xlsx" % plate.name)

    Parameters
    ----------

    filepath
      Path to the Geneart excel spreadsheet.
    """
    plates_data = pandas.read_excel(filepath, skiprows=3)  # skip the first 3 rows
    plates_indices = sorted(set(plates_data.Plate))  # there may be multiple plates
    plates = {index: Plate96(name="Plate %d" % index) for index in plates_indices}
    for index, plate in plates.items():
        subdata = plates_data[plates_data.Plate == index]
        for i, row in subdata.iterrows():
            well = plate.wells[row.Pos]
            well.data = {k: row[k] for k in ("IDAuftrag", "IDConstruct")}
            volume_microl = row["Volume [µl]"]
            volume_in_l = volume_microl * 1e-6
            quantity = volume_microl * row["Concentration [µg/µl]"] * 1e-6
            part_label = row.Gene_Name
            well.add_content({part_label: quantity}, volume=volume_in_l)

    return [plate for i, plate in sorted(plates.items())]


def make_csv_from_fragment_analyzer_report(
    filepath,
    destination_plate_name="ENTER DESTINATION PLATE NAME",
    destination_plate_type="ENTER DESTINATION PLATE TYPE",
    destination_plate_size=96,
    volume_to_transfer="ENTER VOLUME TO TRANSFER (uL)",  # microliter
    destination_csv=None,
    source_plate_name="ENTER SOURCE PLATE NAME",
    source_plate_type="ENTER SOURCE PLATE TYPE",
    source_plate_size=96,
):
    df = pandas.read_csv(filepath)

    if any(pandas.isna(df.best_clone)):
        raise ValueError("Missing 'best_clone'. Delete rows that are not needed.")

    plate_data = df[["construct", "best_clone"]]

    plate_data = plate_data.rename(
        columns={"construct": "source_well_content", "best_clone": "source_well"}
    )

    plate_data["source_well_concentration"] = ""

    plate_data["source_plate_size"] = source_plate_size
    plate_data["volume_to_transfer"] = volume_to_transfer
    plate_data["source_plate_name"] = source_plate_name
    plate_data["source_plate_type"] = source_plate_type
    plate_data["destination_plate_name"] = destination_plate_name
    plate_data["destination_plate_type"] = destination_plate_type
    plate_data["destination_plate_size"] = destination_plate_size

    if destination_csv is not None:
        plate_data.to_csv(destination_csv, index=False)

    return plate_data
