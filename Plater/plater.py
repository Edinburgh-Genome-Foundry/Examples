import pandas
import plateo
from plateo.containers import Plate96, Plate384
import dioscuri


def create_gwl_and_platemap_from_csv(
    name, csv_file, starting_well=1, washing_scheme=None
):
    """Generate a dioscuri.GeminiWorkList() from a csv file.

    **Parameters**

    **name**
    > Name of the project.

    **csv_file**
    > The csv file containing the transfers. There must be only one destination plate
    > specified. The required csv columns are:
        source_well
        source_well_content
        source_well_concentration
        source_well_volume
        source_plate_name
        source_plate_type
        source_plate_size
        volume_to_transfer
        destination_plate_name
        destination_plate_type
        destination_plate_size

    **starting_well**
    > The index of the starting well. Wells up to that well will be skipped. Default 1.

    **washing_scheme**
    > The washing_scheme to use between the transfers. Default parameter uses "W".
    """
    df = read_transfer_table(csv_file)
    if not len(set(df.destination_plate_name)) == 1:
        raise ValueError("There must be only one destination plate specified")

    gwl = create_worklist_data_object(name, df, starting_well, washing_scheme)

    destination_well_list = list(
        range(starting_well, len(df.destination_plate_type) + 1)
    )
    wellnames = [
        plateo.tools.index_to_wellname(
            index=index, num_wells=df.destination_plate_size[0], direction="column"
        )
        for index in destination_well_list
    ]
    df["destination_well"] = wellnames

    try:
        plate = create_destination_plate(name, df, starting_well)
    except ValueError:
        print("Cannot create destination plate: missing content")

    return {"gwl": gwl, "plate": plate}


def read_transfer_table(filename):
    list_of_transfers_in_table = pandas.read_csv(filename)

    return list_of_transfers_in_table


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


def create_destination_plate(name, df, starting_well):
    if any(pandas.isna(df.source_well_content)):
        raise ValueError

    if any(pandas.isna(df.source_well_concentration)):
        raise ValueError

    if df.destination_plate_size[0] == 96:
        plate = Plate96(name=name)
    elif df.destination_plate_size[0] == 384:
        plate = Plate384(name=name)
    else:
        raise ValueError("Only 96-well and 384-well destination plates are supported.")

    for i, row in df.iterrows():
        well = plate.wells[row.destination_well]
        well.data = {"source_well_content": row.source_well_content}
        volume_microl = row["volume_to_transfer"]  # microliter (uL)
        volume_in_l = volume_microl * 1e-6
        quantity = volume_microl * row["source_well_concentration"] * 1e-9  # ng / uL
        part_label = row.source_well_content
        well.add_content({part_label: quantity}, volume=volume_in_l)

    return plate
    # """CREATE DF"""
    # number_of_transfers = len(df.well)
    # dict_of_series = {
    #     "source_well": df.well,
    #     "name": df.name,
    #     "concentration": df.concentration,
    #     "source_plate_name": pandas.Series([source_plate_name] * number_of_transfers),
    #     "source_plate_type": pandas.Series([source_plate_type] * number_of_transfers),
    #     "source_plate_tecan_well": pandas.Series(source_plate_tecan_well_list),
    #     "destination_plate_name": pandas.Series([destination_plate_name] * number_of_transfers),
    #     "destination_plate_type": pandas.Series([destination_plate_type] * number_of_transfers),
    #     "destination_well": pandas.Series(destination_well_list),
    # }
    # output_df = pandas.DataFrame(dict_of_series)


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

    # name_well_dict = dict(zip(df.name, df.well))

    # # source_plate_name_list = []
    # # source_plate_type_list = []
    # source_plate_tecan_well_list = []
    # # destination_plate_name_list = []
    # # destination_plate_type_list = []
    # destination_well_list = []

    # for name, well in name_well_dict.items():

    # """GENERATE GWL"""

    # tecan_well = convert_plate96_to_tecan_well(well)
    # #         print(tecan_well)
    # aspirate = dioscuri.Pipette(
    #     "A",
    #     rack_label=source_plate_name,
    #     rack_type=source_plate_type,
    #     position=tecan_well,
    #     volume=volume,
    # )
    # records.append(aspirate)

    # dispense = dioscuri.Pipette(
    #     "D",
    #     rack_label=destination_plate_name,
    #     rack_type=destination_plate_type,
    #     position=current_destination_well,
    #     volume=volume,
    # )
    # records.append(dispense)

    # records.append(wash)

    # worklist = dioscuri.GeminiWorkList(name=name, records=records)

    # """Store to make pandas Series"""
    # #         source_plate_name_list.append(source_plate_name)
    # #         source_plate_type_list.append(source_plate_type)
    # source_plate_tecan_well_list.append(tecan_well)
    # #         destination_plate_name_list.append(destination_plate_name)
    # #         destination_plate_type_list.append(destination_plate_type)
    # destination_well_list.append(current_destination_well)

    # """CREATE DF"""
    # number_of_transfers = len(df.well)
    # dict_of_series = {
    #     "source_well": df.well,
    #     "name": df.name,
    #     "concentration": df.concentration,
    #     "source_plate_name": pandas.Series([source_plate_name] * number_of_transfers),
    #     "source_plate_type": pandas.Series([source_plate_type] * number_of_transfers),
    #     "source_plate_tecan_well": pandas.Series(source_plate_tecan_well_list),
    #     "destination_plate_name": pandas.Series(
    #         [destination_plate_name] * number_of_transfers
    #     ),
    #     "destination_plate_type": pandas.Series(
    #         [destination_plate_type] * number_of_transfers
    #     ),
    #     "destination_well": pandas.Series(destination_well_list),
    # }
    # output_df = pandas.DataFrame(dict_of_series)

    # return {"worklist": worklist, "output_df": output_df}

    return worklist


def convert_geneart_shipment_file_to_csv(
    filepath,
    destination_plate_name,
    destination_plate_type,
    destination_plate_size,
    volume_to_transfer=50,
):
    """Create a csv file from a shipment layout sheet.

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
    plates_data["volume_to_transfer"] = volume_to_transfer
    plates_data["source_plate_type"] = "ENTER SOURCE PLATE TYPE"
    plates_data["destination_plate_name"] = destination_plate_name
    plates_data["destination_plate_type"] = destination_plate_type
    plates_data["destination_plate_size"] = destination_plate_size
    csv_filepath = filepath + ".csv"
    plates_data.to_csv(csv_filepath, index=False)


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
