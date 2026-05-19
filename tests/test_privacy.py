from pathlib import Path

from dataorchestra.privacy import scan_csv_files


def test_privacy_blocks_email_values(tmp_path: Path):
    csv_path = tmp_path / "ventas.csv"
    csv_path.write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario,contacto\n"
        "2026-01-01,Producto A,Categoria 1,1,100,70,persona@example.com\n",
        encoding="utf-8",
    )

    report = scan_csv_files([csv_path])

    assert report.status == "blocked_privacy_review"
    assert report.safe_to_continue is False
    assert any(finding.evidence == "<email>" for finding in report.findings)
    assert any(finding.reason == "sensitive_column_name" for finding in report.findings)


def test_privacy_passes_anonymized_template(tmp_path: Path):
    csv_path = tmp_path / "ventas.csv"
    csv_path.write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario\n"
        "2026-01-01,Producto A,Categoria 1,1,100,70\n",
        encoding="utf-8",
    )

    report = scan_csv_files([csv_path])

    assert report.status == "passed"
    assert report.safe_to_continue is True
    assert report.findings == []


def test_privacy_blocks_composed_sensitive_column_names(tmp_path: Path):
    csv_path = tmp_path / "ventas.csv"
    csv_path.write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario,email_cliente\n"
        "2026-01-01,Producto A,Categoria 1,1,100,70,\n",
        encoding="utf-8",
    )

    report = scan_csv_files([csv_path])

    assert report.status == "blocked_privacy_review"
    assert report.safe_to_continue is False
    assert report.findings[0].reason == "sensitive_column_name"
