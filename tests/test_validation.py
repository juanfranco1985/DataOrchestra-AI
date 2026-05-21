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


def test_validation_blocks_advanced_high_commercial_issues(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    write_valid_client(raw_dir)
    (raw_dir / "ventas.csv").write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario\n"
        "1999-12-31,Producto X,Categoria 1,1,100,70\n"
        "2026-01-02,Producto A,Categoria 1,1,0,70\n",
        encoding="utf-8",
    )

    report = validate_client_raw(raw_dir)
    codes = {issue.code for issue in report.issues}

    assert report.status == "blocked"
    assert report.can_continue is False
    assert "date_out_of_supported_range" in codes
    assert "sold_product_missing_from_catalog" in codes
    assert "impossible_margin_zero_price_with_cost" in codes


def test_validation_flags_advanced_medium_commercial_warnings_without_blocking(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "ventas.csv").write_text(
        "fecha,producto,categoria,cantidad,precio_unitario,costo_unitario\n"
        "2026-01-01,Producto A,Categoria Distinta,1,50,70\n"
        "2026-01-01,Producto A,Categoria Distinta,1,50,70\n"
        "2026-01-02,Producto A,Categoria 1,1,100,70\n",
        encoding="utf-8",
    )
    (raw_dir / "productos.csv").write_text(
        "producto,categoria,precio_unitario,costo_unitario\n"
        "Producto A,Categoria 1,100,70\n"
        "Producto AA,Categoria 1,100,70\n",
        encoding="utf-8",
    )
    (raw_dir / "stock.csv").write_text(
        "producto,stock_actual,stock_minimo,ventas_ultimos_30_dias\n"
        "Producto A,0,2,4\n"
        "Producto AA,10,2,4\n",
        encoding="utf-8",
    )

    report = validate_client_raw(raw_dir)
    codes = {issue.code for issue in report.issues}

    assert report.status == "passed"
    assert report.can_continue is True
    assert "unit_price_below_cost" in codes
    assert "duplicate_sales_row" in codes
    assert "zero_stock_with_recent_sales" in codes
    assert "stock_below_minimum" in codes
    assert "category_mismatch_with_catalog" in codes
    assert "inconsistent_sales_category_for_product" in codes
    assert "near_duplicate_product_name" in codes
