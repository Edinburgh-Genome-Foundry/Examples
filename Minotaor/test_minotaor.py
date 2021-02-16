import minotaor


def test_annotate_record():
    protein = minotaor.Seq("HHHHHHDLG*EDINBURGHGENQMEFQUNDRY*")
    protein_record = minotaor.SeqRecord(
        protein, id="example", annotations={"molecule_type": "protein"}
    )

    protein_record = minotaor.annotate_record(protein_record)

    assert len(protein_record.features) == 4
    assert protein_record.features[0].id == "no start codon"
    assert protein_record.features[1].id == "STOP"
    assert protein_record.features[3].id == "6xHis"
