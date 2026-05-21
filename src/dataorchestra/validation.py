from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import csv
from pathlib import Path
from typing import Iterable

from dataorchestra.contracts import DATA_CONTRACT_VERSION, expected_files, validation_schema


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
