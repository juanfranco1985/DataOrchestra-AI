from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
from pathlib import Path
import re
from typing import Iterable


SENSITIVE_COLUMN_KEYWORDS = {
    "apellido",
    "alias",
    "banco",
    "cbu",
    "cliente_nombre",
    "contacto",
    "correo",
    "cuenta",
    "cuil",
    "cuit",
    "direccion",
    "dni",
    "email",
    "mail",
    "nombre",
    "password",
    "telefono",
    "tarjeta",
}

VALUE_PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "cuit_cuil": re.compile(r"\b\d{2}-?\d{8}-?\d\b"),
    "credit_card_like": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    "phone_like": re.compile(r"\b(?:\+?\d{1,3}[- ]?)?(?:\d[- ]?){9,14}\b"),
}


@dataclass(frozen=True)
class PrivacyFinding:
    file: str
    column: str
    severity: str
    reason: str
    evidence: str


@dataclass(frozen=True)
class PrivacyReport:
    status: str
    safe_to_continue: bool
    findings: list[PrivacyFinding]
    files_checked: list[str]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "safe_to_continue": self.safe_to_continue,
            "findings": [asdict(item) for item in self.findings],
            "files_checked": self.files_checked,
        }


def normalize_name(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def scan_csv_files(paths: Iterable[str | Path], sample_rows: int = 200) -> PrivacyReport:
    findings: list[PrivacyFinding] = []
    checked: list[str] = []

    for path_like in paths:
        path = Path(path_like)
        if not path.exists() or path.suffix.lower() != ".csv":
            continue
        checked.append(str(path))
        findings.extend(_scan_headers(path))
        findings.extend(_scan_values(path, sample_rows=sample_rows))

    safe = not findings
    return PrivacyReport(
        status="passed" if safe else "blocked_privacy_review",
        safe_to_continue=safe,
        findings=findings,
        files_checked=checked,
    )


def _scan_headers(path: Path) -> list[PrivacyFinding]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            headers = next(reader)
        except StopIteration:
            return []

    findings: list[PrivacyFinding] = []
    for header in headers:
        normalized = normalize_name(header)
        if is_sensitive_column(normalized):
            findings.append(
                PrivacyFinding(
                    file=str(path),
                    column=header,
                    severity="high",
                    reason="sensitive_column_name",
                    evidence="<column_name_only>",
                )
            )
    return findings


def is_sensitive_column(normalized_header: str) -> bool:
    if normalized_header in SENSITIVE_COLUMN_KEYWORDS:
        return True
    parts = {part for part in re.split(r"[_\s]+", normalized_header) if part}
    if parts.intersection(SENSITIVE_COLUMN_KEYWORDS):
        return True
    return any(keyword in normalized_header for keyword in {"email", "telefono", "direccion", "password"})


def _scan_values(path: Path, sample_rows: int) -> list[PrivacyFinding]:
    findings: list[PrivacyFinding] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader):
            if index >= sample_rows:
                break
            for column, raw_value in row.items():
                value = str(raw_value or "")
                for pattern_name, pattern in VALUE_PATTERNS.items():
                    if pattern.search(value):
                        findings.append(
                            PrivacyFinding(
                                file=str(path),
                                column=column or "",
                                severity="high",
                                reason=f"sensitive_value_pattern:{pattern_name}",
                                evidence=f"<{pattern_name}>",
                            )
                        )
    return findings
