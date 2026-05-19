from pathlib import Path

from dataorchestra.integrity import fingerprint_file, fingerprint_files


def test_fingerprint_file_records_sha256_size_and_name(tmp_path: Path):
    path = tmp_path / "ventas.csv"
    path.write_text("abc", encoding="utf-8")

    fingerprint = fingerprint_file(path)

    assert fingerprint.name == "ventas.csv"
    assert fingerprint.size_bytes == 3
    assert fingerprint.sha256 == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert fingerprint.modified_at_utc.endswith("+00:00")


def test_fingerprint_files_sorts_paths_for_stable_reports(tmp_path: Path):
    second = tmp_path / "stock.csv"
    first = tmp_path / "productos.csv"
    second.write_text("stock", encoding="utf-8")
    first.write_text("productos", encoding="utf-8")

    fingerprints = fingerprint_files([second, first])

    assert [item["name"] for item in fingerprints] == ["productos.csv", "stock.csv"]
