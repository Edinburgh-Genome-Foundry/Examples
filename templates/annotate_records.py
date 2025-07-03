# Add sequence names as feature annotations
import dnacauldron as dc
from Bio import SeqFeature
from Bio.SeqFeature import SeqFeature, FeatureLocation

records = dc.biotools.load_records_from_files(files=["sequences.fa"], use_file_names_as_ids=False)

for record in records:
        record.features.append(
            SeqFeature(
                FeatureLocation(0, len(record)),
                id=record.id,
                type="misc_feature",
                qualifiers={"label": record.id, "note": record.id},
            )
        )
