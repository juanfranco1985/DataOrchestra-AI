from pathlib import Path

from dataorchestra.validation import validate_client_raw


def write_valid_client(raw_dir: Path) -> None:
    raw_dir.mkdir(parents=True)
    (raw_dir / "ventas.csv").write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario\n"
        "2026-01-01,Producto A,Categoria 1,1,100,70\n",
        encoding="utf-8",
    )
    (raw_dir / "productos.csv").write_text(
        "producto,categoria,precio_unitario,costo_unitario\n"
        "Producto A,Categoria 1,100,70\n",
        encoding="utf-8",
    )
    (raw_dir / "stock.csv").write_text(
        "producto,stock_actual,stock_minimo,ventas_ultimos_30_dias\n"
        "Producto A,10,2,4\n",
        encoding="utf-8",
    )


def test_validation_passes_valid_raw_files(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    write_valid_client(raw_dir)

    report = validate_client_raw(raw_dir)

    assert report.status == "passed"
    assert report.can_continue is True
    assert report.issues == []


def test_validation_blocks_missing_required_file(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "ventas.csv").write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario\n"
        "2026-01-01,Producto A,Categoria 1,1,100,70\n",
        encoding="utf-8",
    )

    report = validate_client_raw(raw_dir)

    assert report.status == "blocked"
    assert report.can_continue is False
    assert any(issue.code == "missing_file" for issue in report.issues)


def test_validation_blocks_invalid_dates_numbers_and_empty_required_values(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    write_valid_client(raw_dir)
    (raw_dir / "ventas.csv").write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario\n"
        "01/01/2026,Producto A,Categoria 1,1,100,70\n"
        "2026-01-02,Producto B,Categoria 1,-2,100,70\n"
        "2026-01-03,,Categoria 1,1,abc,70\n",
        encoding="utf-8",
    )

    report = validate_client_raw(raw_dir)
    codes = {issue.code for issue in report.issues}

    assert report.status == "blocked"
    assert report.can_continue is False
    assert "invalid_date" in codes
    assert "negative_number" in codes
    assert "invalid_number" in codes
    assert "empty_required_value" in codes
