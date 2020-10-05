"""Classes for representing a Gemini WorkList (gwl).

The gwl file specification is based on the
Freedom EVOware Software Manual, 393172, v2.3 (2009).

DiTi is short for 'Disposable Tip'.
"""


class GeminiWorkList:
    def __init__(self, name="worklist", records=None):
        self.name = name
        if records is None:
            self.records = []
        else:
            self.records = records

    def add_record(self, record):
        self.records.append(record)

    def list_records(self):
        for record in self.records:
            # call readable print of record
            pass

    def records_to_string(self):
        records_as_string = ""
        for record in self.records:
            # call record.to_string()
            # records_as_string += record.to_string()
            records_as_string += "\n"
            pass

        return records_as_string


class Aspirate:
    def __init__(
        self,
        rack_label,
        rack_type,
        position,
        volume,
        tube_id="",
        rack_id="",
        liquid_class="",
        tip_mask="",
        forced_rack_type="",
    ):

        self.type_character = "A"  # Determined by gwl specification

        self.rack_label = rack_label
        self.rack_id = rack_id
        self.rack_type = rack_type
        self.position = position
        self.tube_id = tube_id
        self.volume = volume
        self.liquid_class = liquid_class
        self.tip_mask = tip_mask
        self.forced_rack_type = forced_rack_type

        self.tip_type = ""  # Reserved, must be omitted.

    def to_string(self):
        parameters = [
            self.type_character,
            self.rack_label,
            self.rack_id,
            self.rack_type,
            self.position,
            self.tube_id,
            self.volume,
            self.liquid_class,
            self.tip_type,
            self.tip_mask,
            self.forced_rack_type,
        ]
        record_as_string = ";".join(parameters,)

        return record_as_string


class Dispense:
    pass


class WashTipOrReplaceDITI:
    pass


class Decontamination:
    pass


class Flush:
    pass


class Break:
    pass


class SetDITIType:
    pass


class Comment:
    pass


class ReagentDistribution:
    pass
