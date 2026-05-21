from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import csv
from difflib import SequenceMatcher
from pathlib import Path
import re
from typing import Iterable

from dataorchestra.contracts import DATA_CONTRACT_VERSION, expected_files, validation_schema


MIN_SUPPORTED_DATE = datetime.fromisoformat("2000-01-01")
MAX_SUPPORTED_DATE = datetime.fromisoformat("2035-12-31")


@dataclass(frozen=True)
class ValidationIssue:
    file: str
    severity: str
    code: str
    message: str
    row: int | None = None
    column: str | None = None


@dataclass(frozen=True)
class ValidationReport:
    status: str
    can_continue: bool
    issues: list[ValidationIssue]
    files_checked: list[str]
    contract_version: str = DATA_CONTRACT_VERSION

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "can_continue": self.can_continue,
            "contract_version": self.contract_version,
            "issues": [asdict(item) for item in self.issues],
            "files_checked": self.files_checked,
        }


def validate_client_raw(raw_dir: str | Path) -> ValidationReport:
    raw = Path(raw_dir)
    expected = {dataset: raw / file_name for dataset, file_name in expected_files().items()}
    issues: list[ValidationIssue] = []
    checked: list[str] = []

    for dataset, path in expected.items():
        if not path.exists():
            issues.append(
                ValidationIssue(
                    file=str(path),
                    severity="high",
                    code="missing_file",
                    message=f"Missing required file: {path.name}",
                )
            )
            continue
        checked.append(str(path))
        issues.extend(validate_csv_schema(path, dataset))

    if not any(issue.severity == "high" for issue in issues):
        issues.extend(validate_commercial_consistency(raw))

    blocking = any(issue.severity == "high" for issue in issues)
    return ValidationReport(
        status="blocked" if blocking else "passed",
        can_continue=not blocking,
        issues=issues,
        files_checked=checked,
    )


def validate_csv_schema(path: str | Path, dataset: str) -> list[ValidationIssue]:
    schema = validation_schema(dataset)
    file_path = Path(path)
    issues: list[ValidationIssue] = []

    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = {normalize_name(item) for item in (reader.fieldnames or [])}
        missing = sorted(schema["required"] - headers)
        for column in missing:
            issues.append(
                ValidationIssue(
                    file=str(file_path),
                    severity="high",
                    code="missing_required_column",
                    message=f"Missing required column: {column}",
                    column=column,
                )
            )
        if missing:
            return issues

        for row_number, row in enumerate(reader, start=2):
            normalized_row = {normalize_name(k): v for k, v in row.items()}
            issues.extend(_validate_required_values(file_path, normalized_row, row_number, schema["required"]))
            issues.extend(_validate_numeric(file_path, normalized_row, row_number, schema["numeric_non_negative"]))
            issues.extend(_validate_dates(file_path, normalized_row, row_number, schema["date"]))

    return issues


def validate_commercial_consistency(raw_dir: str | Path) -> list[ValidationIssue]:
    raw = Path(raw_dir)
    ventas_path = raw / "ventas.csv"
    productos_path = raw / "productos.csv"
    stock_path = raw / "stock.csv"

    sales_rows = _read_rows(ventas_path)
    product_rows = _read_rows(productos_path)
    stock_rows = _read_rows(stock_path)
    issues: list[ValidationIssue] = []

    issues.extend(_validate_date_range(ventas_path, sales_rows))
    issues.extend(_validate_sold_products_exist_in_catalog(ventas_path, sales_rows, product_rows))
    issues.extend(_validate_price_cost_relationships(ventas_path, sales_rows, productos_path, product_rows))
    issues.extend(_validate_duplicate_sales_rows(ventas_path, sales_rows))
    issues.extend(_validate_stock_logic(stock_path, stock_rows))
    issues.extend(_validate_category_consistency(ventas_path, sales_rows, productos_path, product_rows))
    issues.extend(_validate_near_duplicate_products(product_rows, stock_rows, productos_path, stock_path))
    return issues


def normalize_name(value: str | None) -> str:
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def _validate_required_values(path: Path, row: dict[str, str], row_number: int, columns: Iterable[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for column in columns:
        if str(row.get(column, "")).strip() == "":
            issues.append(
                ValidationIssue(
                    file=str(path),
                    severity="high",
                    code="empty_required_value",
                    message=f"Empty required value in {column}",
                    row=row_number,
                    column=column,
                )
            )
    return issues


def _validate_numeric(path: Path, row: dict[str, str], row_number: int, columns: Iterable[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for column in columns:
        value = str(row.get(column, "")).strip().replace(",", ".")
        try:
            number = float(value)
        except ValueError:
            issues.append(
                ValidationIssue(
                    file=str(path),
                    severity="high",
                    code="invalid_number",
                    message=f"Invalid numeric value in {column}",
                    row=row_number,
                    column=column,
                )
            )
            continue
        if number < 0:
            issues.append(
                ValidationIssue(
                    file=str(path),
                    severity="high",
                    code="negative_number",
                    message=f"Negative value in {column}",
                    row=row_number,
                    column=column,
                )
            )
    return issues


def _validate_dates(path: Path, row: dict[str, str], row_number: int, columns: Iterable[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for column in columns:
        value = str(row.get(column, "")).strip()
        try:
            datetime.fromisoformat(value)
        except ValueError:
            issues.append(
                ValidationIssue(
                    file=str(path),
                    severity="high",
                    code="invalid_date",
                    message=f"Invalid ISO date in {column}. Expected YYYY-MM-DD.",
                    row=row_number,
                    column=column,
                )
            )
    return issues


def _validate_date_range(path: Path, rows: list[dict[str, str]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for row_number, row in enumerate(rows, start=2):
        value = str(row.get("fecha", "")).strip()
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            continue
        if parsed < MIN_SUPPORTED_DATE or parsed > MAX_SUPPORTED_DATE:
            issues.append(
                ValidationIssue(
                    file=str(path),
                    severity="high",
                    code="date_out_of_supported_range",
                    message=f"Date outside supported range {MIN_SUPPORTED_DATE.date()} to {MAX_SUPPORTED_DATE.date()}.",
                    row=row_number,
                    column="fecha",
                )
            )
    return issues


def _validate_sold_products_exist_in_catalog(path: Path, sales_rows: list[dict[str, str]], product_rows: list[dict[str, str]]) -> list[ValidationIssue]:
    catalog_products = {row.get("producto", "") for row in product_rows if row.get("producto")}
    issues: list[ValidationIssue] = []
    for row_number, row in enumerate(sales_rows, start=2):
        product = row.get("producto", "")
        if product and product not in catalog_products:
            issues.append(
                ValidationIssue(
                    file=str(path),
                    severity="high",
                    code="sold_product_missing_from_catalog",
                    message=f"Sold product is missing from productos.csv: {product}",
                    row=row_number,
                    column="producto",
                )
            )
    return issues


def _validate_price_cost_relationships(
    ventas_path: Path,
    sales_rows: list[dict[str, str]],
    productos_path: Path,
    product_rows: list[dict[str, str]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for row_number, row in enumerate(sales_rows, start=2):
        price = _number(row.get("precio_unitario"))
        cost = _number(row.get("costo_unitario"))
        if price is None or cost is None:
            continue
        if price == 0 and cost > 0:
            issues.append(
                ValidationIssue(
                    file=str(ventas_path),
                    severity="high",
                    code="impossible_margin_zero_price_with_cost",
                    message="Sale has zero price with positive cost; margin cannot be interpreted.",
                    row=row_number,
                    column="precio_unitario",
                )
            )
        elif price < cost:
            issues.append(
                ValidationIssue(
                    file=str(ventas_path),
                    severity="medium",
                    code="unit_price_below_cost",
                    message="Sale unit price is lower than unit cost; confirm if this is intentional.",
                    row=row_number,
                    column="precio_unitario",
                )
            )

    for row_number, row in enumerate(product_rows, start=2):
        price = _number(row.get("precio_unitario"))
        cost = _number(row.get("costo_unitario"))
        if price is None or cost is None:
            continue
        if price == 0 and cost > 0:
            issues.append(
                ValidationIssue(
                    file=str(productos_path),
                    severity="high",
                    code="catalog_impossible_margin_zero_price_with_cost",
                    message="Catalog has zero price with positive cost; margin cannot be interpreted.",
                    row=row_number,
                    column="precio_unitario",
                )
            )
        elif price < cost:
            issues.append(
                ValidationIssue(
                    file=str(productos_path),
                    severity="medium",
                    code="catalog_price_below_cost",
                    message="Catalog unit price is lower than unit cost; confirm if this is intentional.",
                    row=row_number,
                    column="precio_unitario",
                )
            )
    return issues


def _validate_duplicate_sales_rows(path: Path, sales_rows: list[dict[str, str]]) -> list[ValidationIssue]:
    first_seen: dict[tuple[tuple[str, str], ...], int] = {}
    issues: list[ValidationIssue] = []
    for row_number, row in enumerate(sales_rows, start=2):
        key = tuple(sorted((key, str(value or "").strip()) for key, value in row.items()))
        if key in first_seen:
            issues.append(
                ValidationIssue(
                    file=str(path),
                    severity="medium",
                    code="duplicate_sales_row",
                    message=f"Possible duplicated sales row. First occurrence at row {first_seen[key]}.",
                    row=row_number,
                )
            )
        else:
            first_seen[key] = row_number
    return issues


def _validate_stock_logic(path: Path, stock_rows: list[dict[str, str]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for row_number, row in enumerate(stock_rows, start=2):
        stock_actual = _number(row.get("stock_actual"))
        stock_minimo = _number(row.get("stock_minimo"))
        recent_sales = _number(row.get("ventas_ultimos_30_dias"))
        if stock_actual is None or stock_minimo is None or recent_sales is None:
            continue
        if stock_actual == 0 and recent_sales > 0:
            issues.append(
                ValidationIssue(
                    file=str(path),
                    severity="medium",
                    code="zero_stock_with_recent_sales",
                    message="Product has zero current stock but recent sales; confirm stock snapshot timing.",
                    row=row_number,
                    column="stock_actual",
                )
            )
        if stock_minimo > 0 and stock_actual < stock_minimo:
            issues.append(
                ValidationIssue(
                    file=str(path),
                    severity="medium",
                    code="stock_below_minimum",
                    message="Current stock is below configured minimum; confirm if this is expected.",
                    row=row_number,
                    column="stock_actual",
                )
            )
    return issues


def _validate_category_consistency(
    ventas_path: Path,
    sales_rows: list[dict[str, str]],
    productos_path: Path,
    product_rows: list[dict[str, str]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    catalog_categories = {row.get("producto", ""): row.get("categoria", "") for row in product_rows if row.get("producto")}
    seen_sale_categories: dict[str, str] = {}
    for row_number, row in enumerate(sales_rows, start=2):
        product = row.get("producto", "")
        sale_category = row.get("categoria", "")
        if not product:
            continue
        previous = seen_sale_categories.get(product)
        if previous is not None and previous != sale_category:
            issues.append(
                ValidationIssue(
                    file=str(ventas_path),
                    severity="medium",
                    code="inconsistent_sales_category_for_product",
                    message=f"Product appears under multiple categories in ventas.csv: {product}",
                    row=row_number,
                    column="categoria",
                )
            )
        else:
            seen_sale_categories[product] = sale_category

        catalog_category = catalog_categories.get(product)
        if catalog_category is not None and catalog_category != sale_category:
            issues.append(
                ValidationIssue(
                    file=str(ventas_path),
                    severity="medium",
                    code="category_mismatch_with_catalog",
                    message=f"Sales category differs from productos.csv for product: {product}",
                    row=row_number,
                    column="categoria",
                )
            )

    seen_catalog_categories: dict[str, str] = {}
    for row_number, row in enumerate(product_rows, start=2):
        product = row.get("producto", "")
        category = row.get("categoria", "")
        previous = seen_catalog_categories.get(product)
        if product and previous is not None and previous != category:
            issues.append(
                ValidationIssue(
                    file=str(productos_path),
                    severity="medium",
                    code="inconsistent_catalog_category_for_product",
                    message=f"Product appears under multiple categories in productos.csv: {product}",
                    row=row_number,
                    column="categoria",
                )
            )
        elif product:
            seen_catalog_categories[product] = category
    return issues


def _validate_near_duplicate_products(
    product_rows: list[dict[str, str]],
    stock_rows: list[dict[str, str]],
    productos_path: Path,
    stock_path: Path,
) -> list[ValidationIssue]:
    labels: list[tuple[str, Path, int]] = []
    for row_number, row in enumerate(product_rows, start=2):
        product = row.get("producto", "")
        if product:
            labels.append((product, productos_path, row_number))
    for row_number, row in enumerate(stock_rows, start=2):
        product = row.get("producto", "")
        if product:
            labels.append((product, stock_path, row_number))

    issues: list[ValidationIssue] = []
    seen_pairs: set[tuple[str, str]] = set()
    for index, (left, _left_path, _left_row) in enumerate(labels):
        for right, right_path, right_row in labels[index + 1 :]:
            if left == right:
                continue
            pair_key = tuple(sorted((left, right)))
            if pair_key in seen_pairs:
                continue
            if _looks_like_near_duplicate(left, right):
                seen_pairs.add(pair_key)
                issues.append(
                    ValidationIssue(
                        file=str(right_path),
                        severity="medium",
                        code="near_duplicate_product_name",
                        message=f"Possible near-duplicate product names: {left} / {right}",
                        row=right_row,
                        column="producto",
                    )
                )
    return issues


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{normalize_name(key): str(value or "").strip() for key, value in row.items()} for row in reader]


def _number(value: str | None) -> float | None:
    try:
        return float(str(value or "").strip().replace(",", "."))
    except ValueError:
        return None


def _looks_like_near_duplicate(left: str, right: str) -> bool:
    normalized_left = _product_key(left)
    normalized_right = _product_key(right)
    if not normalized_left or not normalized_right:
        return False
    if normalized_left == normalized_right:
        return True
    if min(len(normalized_left), len(normalized_right)) < 4:
        return False
    ratio = SequenceMatcher(None, normalized_left, normalized_right).ratio()
    return ratio >= 0.92


def _product_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").strip().lower())
