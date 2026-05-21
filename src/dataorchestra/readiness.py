from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from dataorchestra.audit import now_iso
from dataorchestra.clients import CLIENT_SUBDIRS
from dataorchestra.states import DiagnosticStatus
from dataorchestra.status import EXPECTED_RAW_FILES, inspect_client_status


CRITICAL_DOCS = (
    "docs/RUNBOOK_PILOTO_REAL.md",
    "docs/PRIVACIDAD_Y_DATOS.md",
    "docs/POLITICA_DATOS_REALES.md",
    "docs/INCIDENTES_OPERATIVOS.md",
    "docs/CALIDAD_DATOS_Y_UMBRALES.md",
)


@dataclass(frozen=True)
class ReadinessCheck:
    id: str
    category: str
    status: str
    severity: str
    message: str
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def inspect_readiness(client_dir: str | Path, repo_root: str | Path | None = None) -> dict[str, Any]:
    client_path = Path(client_dir)
    repo_path = Path(repo_root) if repo_root is not None else None
    checks: list[ReadinessCheck] = []

    checks.extend(_workspace_checks(client_path))

    status = inspect_client_status(client_path) if client_path.exists() else None
    if status:
        checks.extend(_raw_file_checks(status))
        checks.extend(_preflight_checks(status))
        checks.extend(_data_quality_checks(status))
        checks.extend(_review_gate_checks(status))
        checks.extend(_incident_checks(status))
        checks.extend(_closure_checks(status))
    else:
        checks.append(
            _fail(
                "client_status_unavailable",
                "workspace",
                "No se pudo inspeccionar el estado del cliente.",
                {"client_dir": str(client_path)},
            )
        )

    if repo_path is not None:
        checks.extend(_repository_checks(repo_path))
        checks.extend(_runtime_location_checks(client_path, repo_path))

    failures = [check for check in checks if check.status == "fail"]
    warnings = [check for check in checks if check.status == "warn"]

    return {
        "generated_at": now_iso(),
        "client_id": status["client_id"] if status else client_path.name,
        "client_dir": str(client_path),
        "current_stage": status["current_stage"] if status else "unknown",
        "overall_status": "blocked" if failures else "ready_with_warnings" if warnings else "ready",
        "can_continue": not failures,
        "failure_count": len(failures),
        "warning_count": len(warnings),
        "checks": [check.to_dict() for check in checks],
        "next_action": _recommended_action(failures, warnings, status),
    }


def _workspace_checks(client_path: Path) -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = []

    if not client_path.exists():
        return [
            _fail(
                "client_dir_missing",
                "workspace",
                "La carpeta del cliente no existe.",
                {"client_dir": str(client_path)},
            )
        ]

    checks.append(_pass("client_dir_exists", "workspace", "La carpeta del cliente existe.", {"client_dir": str(client_path)}))

    for subdir in CLIENT_SUBDIRS:
        target = client_path / subdir
        if target.exists() and target.is_dir():
            checks.append(_pass(f"{subdir}_dir_exists", "workspace", f"Existe la carpeta {subdir}/.", {"path": str(target)}))
        else:
            checks.append(_fail(f"{subdir}_dir_missing", "workspace", f"Falta la carpeta operativa {subdir}/.", {"path": str(target)}))

    config_path = client_path / "client.yaml"
    if config_path.exists():
        checks.append(_pass("client_config_exists", "workspace", "Existe client.yaml.", {"path": str(config_path)}))
    else:
        checks.append(_fail("client_config_missing", "workspace", "Falta client.yaml.", {"path": str(config_path)}))

    return checks


def _raw_file_checks(status: dict[str, Any]) -> list[ReadinessCheck]:
    raw_files = status["raw_files"]
    checks: list[ReadinessCheck] = []

    if raw_files["missing"]:
        checks.append(
            _fail(
                "raw_files_missing",
                "data",
                "Faltan archivos raw obligatorios.",
                {"missing": raw_files["missing"], "expected": list(EXPECTED_RAW_FILES)},
            )
        )
    else:
        checks.append(_pass("raw_files_complete", "data", "Estan los tres CSV obligatorios.", {"present": raw_files["present"]}))

    extra_files = sorted(set(raw_files["present"]) - set(EXPECTED_RAW_FILES))
    if extra_files:
        checks.append(
            _warn(
                "extra_raw_csv_files",
                "data",
                "Hay CSV adicionales en raw/. Confirmar que no contienen datos sensibles ni se procesan por error.",
                {"extra_files": extra_files},
            )
        )

    return checks


def _preflight_checks(status: dict[str, Any]) -> list[ReadinessCheck]:
    preflight = status["preflight"]
    if not preflight["exists"]:
        return [_fail("preflight_missing", "preflight", "Falta ejecutar preflight.", {})]

    if preflight.get("status") != DiagnosticStatus.READY_FOR_ANALYSIS.value:
        return [
            _fail(
                "preflight_not_ready",
                "preflight",
                "El preflight no esta listo para analisis.",
                {"status": preflight.get("status"), "run_id": preflight.get("run_id")},
            )
        ]

    return [
        _pass(
            "preflight_ready",
            "preflight",
            "El preflight esta listo para analisis.",
            {"run_id": preflight.get("run_id"), "raw_file_count": preflight.get("raw_file_count")},
        )
    ]


def _review_gate_checks(status: dict[str, Any]) -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = []
    analysis = status["analysis"]
    approval = status["approval"]

    if analysis["exists"]:
        if analysis.get("report_status") == DiagnosticStatus.PENDING_HUMAN_REVIEW.value:
            checks.append(
                _pass(
                    "human_review_gate_active",
                    "review",
                    "El borrador esta bloqueado en revision humana.",
                    {"run_id": analysis.get("run_id"), "report_status": analysis.get("report_status")},
                )
            )
        else:
            checks.append(
                _warn(
                    "analysis_report_status_unexpected",
                    "review",
                    "El estado del reporte de analisis no es el esperado.",
                    {"report_status": analysis.get("report_status")},
                )
            )
    else:
        checks.append(_warn("analysis_not_generated", "review", "Todavia no hay borrador de analisis.", {}))

    if approval["exists"]:
        checks.append(
            _pass(
                "approval_record_exists",
                "review",
                "Existe registro de aprobacion humana.",
                {"reviewer": approval.get("reviewer"), "approved_at": approval.get("approved_at")},
            )
        )
    else:
        checks.append(_warn("approval_missing", "review", "No existe aprobacion humana registrada todavia.", {}))

    return checks


def _data_quality_checks(status: dict[str, Any]) -> list[ReadinessCheck]:
    data_quality = status.get("data_quality", {})
    if not data_quality.get("exists"):
        return [_warn("data_quality_missing", "data_quality", "Falta calcular score de calidad de datos.", {})]

    if data_quality.get("can_support_diagnostic") is False:
        return [
            _fail(
                "data_quality_below_target",
                "data_quality",
                "El score de calidad esta por debajo del objetivo recomendado.",
                {
                    "score": data_quality.get("score"),
                    "target_score": data_quality.get("target_score"),
                    "level": data_quality.get("level"),
                    "finding_count": data_quality.get("finding_count"),
                },
            )
        ]

    return [
        _pass(
            "data_quality_ok",
            "data_quality",
            "El score de calidad permite interpretar el diagnostico.",
            {"score": data_quality.get("score"), "target_score": data_quality.get("target_score"), "level": data_quality.get("level")},
        )
    ]


def _closure_checks(status: dict[str, Any]) -> list[ReadinessCheck]:
    closure = status["closure"]
    if not closure["exists"]:
        return [_warn("pilot_not_closed", "closure", "El piloto aun no tiene cierre operativo registrado.", {})]

    if closure.get("data_retention_action_required"):
        return [
            _warn(
                "retention_review_required",
                "closure",
                "El cierre requiere revisar retencion o borrado de datos.",
                {"outcome": closure.get("outcome"), "closed_at": closure.get("closed_at")},
            )
        ]

    return [_pass("pilot_closed", "closure", "El piloto esta cerrado.", {"outcome": closure.get("outcome")})]


def _incident_checks(status: dict[str, Any]) -> list[ReadinessCheck]:
    incidents = status.get("incidents", {})
    if incidents.get("blocking_open_count", 0) > 0:
        return [
            _fail(
                "blocking_incidents_open",
                "incidents",
                "Hay incidentes abiertos que bloquean el flujo.",
                {
                    "open_count": incidents.get("open_count"),
                    "blocking_open_count": incidents.get("blocking_open_count"),
                    "latest": incidents.get("latest"),
                },
            )
        ]
    if incidents.get("open_count", 0) > 0:
        return [
            _warn(
                "incidents_open",
                "incidents",
                "Hay incidentes abiertos de baja severidad. Revisar antes de entregar.",
                {"open_count": incidents.get("open_count"), "latest": incidents.get("latest")},
            )
        ]
    if incidents.get("count", 0) > 0:
        return [_pass("incidents_reviewed", "incidents", "No hay incidentes abiertos.", {"count": incidents.get("count")})]
    return [_pass("no_incidents_registered", "incidents", "No hay incidentes registrados.", {})]


def _repository_checks(repo_path: Path) -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = []
    for relative in CRITICAL_DOCS:
        path = repo_path / relative
        if path.exists():
            checks.append(_pass(f"doc_{path.stem}_exists", "documentation", f"Existe {relative}.", {"path": str(path)}))
        else:
            checks.append(_fail(f"doc_{path.stem}_missing", "documentation", f"Falta documentacion critica: {relative}.", {"path": str(path)}))
    return checks


def _runtime_location_checks(client_path: Path, repo_path: Path) -> list[ReadinessCheck]:
    try:
        relative = client_path.resolve().relative_to(repo_path.resolve())
    except ValueError:
        return [_pass("client_outside_repo", "runtime", "La carpeta del cliente esta fuera del repositorio.", {"client_dir": str(client_path)})]

    if str(relative).replace("\\", "/").startswith("clients/"):
        return [
            _warn(
                "client_inside_repo_clients_dir",
                "runtime",
                "Para datos reales, usar un runtime externo al repositorio en vez de clients/.",
                {"client_dir": str(client_path), "relative_path": str(relative)},
            )
        ]

    return [_pass("client_not_in_repo_clients_dir", "runtime", "La carpeta no esta bajo clients/ del repositorio.", {"relative_path": str(relative)})]


def _recommended_action(failures: list[ReadinessCheck], warnings: list[ReadinessCheck], status: dict[str, Any] | None) -> str:
    if failures:
        first = failures[0]
        return f"Resolver bloqueo: {first.message}"
    if warnings:
        return "Puede continuar, pero revisar advertencias antes de operar con cliente real."
    if status:
        return status["next_action"]
    return "Revisar configuracion del cliente."


def _pass(check_id: str, category: str, message: str, evidence: dict[str, Any]) -> ReadinessCheck:
    return ReadinessCheck(check_id, category, "pass", "info", message, evidence)


def _warn(check_id: str, category: str, message: str, evidence: dict[str, Any]) -> ReadinessCheck:
    return ReadinessCheck(check_id, category, "warn", "medium", message, evidence)


def _fail(check_id: str, category: str, message: str, evidence: dict[str, Any]) -> ReadinessCheck:
    return ReadinessCheck(check_id, category, "fail", "high", message, evidence)
