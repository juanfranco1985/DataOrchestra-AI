from pathlib import Path

from dataorchestra.panel_support import client_label, list_client_dirs, raw_file_table, read_text_preview


def test_list_client_dirs_returns_only_dirs_with_client_yaml(tmp_path: Path):
    client = tmp_path / "clients" / "cliente_001"
    other = tmp_path / "clients" / "sin_config"
    client.mkdir(parents=True)
    other.mkdir()
    (client / "client.yaml").write_text(
        "client:\n  id: cliente_001\n  display_name: Cliente Uno\n",
        encoding="utf-8",
    )

    result = list_client_dirs(tmp_path / "clients")

    assert result == [client]
    assert client_label(client) == "Cliente Uno (cliente_001)"


def test_raw_file_table_reports_expected_files(tmp_path: Path):
    client = tmp_path / "cliente"
    raw = client / "raw"
    raw.mkdir(parents=True)
    (raw / "ventas.csv").write_text("fecha,producto\n", encoding="utf-8")

    rows = raw_file_table(client)

    assert rows[0]["archivo"] == "ventas.csv"
    assert rows[0]["estado"] == "presente"
    assert rows[1]["archivo"] == "productos.csv"
    assert rows[1]["estado"] == "faltante"


def test_read_text_preview_limits_content(tmp_path: Path):
    path = tmp_path / "report.md"
    path.write_text("abcdef", encoding="utf-8")

    assert read_text_preview(path, max_chars=3) == "abc"
    assert read_text_preview(tmp_path / "missing.md") == ""
