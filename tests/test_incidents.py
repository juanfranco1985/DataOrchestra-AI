import json
from pathlib import Path

from dataorchestra.cli import run_incident, run_preflight, run_readiness, run_resolve_incident, run_status
from test_preflight import write_valid_client


def write_incident_client(client_dir: Path) -> None:
    client_dir.mkdir(parents=True)
    (client_dir / "client.yaml").write_text(
        "client:\n"
        "  id: cliente_incident\n",
        encoding="utf-8",
    )


def ensure_operational_dirs(client_dir: Path) -> None:
    for subdir in ("processed", "diagnostics", "reports", "logs", "runs"):
        (client_dir / subdir).mkdir(exist_ok=True)


def test_incident_registration_writes_record_index_and_audit_log(tmp_path: Path):
    client_dir = tmp_path / "cliente_incident"
    write_incident_client(client_dir)

    result = run_incident(
        client_dir,
        incident_type="sensitive_data_detected",
        severity="alta",
        responsible="Responsable Operativo",
        action_taken="Proceso detenido y pedido de version anonimizada.",
        notes="Se registro el tipo de hallazgo sin copiar valores sensibles.",
        requires_data_deletion=True,
        confirm_no_sensitive_values=True,
    )

    assert result["status"] == "incident_registered"
    assert result["flow_blocked"] is True
    assert result["requires_data_deletion"] is True
    record = json.loads(Path(result["incident_record"]).read_text(encoding="utf-8"))
    assert record["incident_type"] == "sensitive_data_detected"
    assert record["incident_status"] == "open"
    assert record["severity"] == "alta"
    index = json.loads((client_dir / "diagnostics" / "incidents" / "incidents_index.json").read_text(encoding="utf-8"))
    assert index["count"] == 1
    assert index["blocking_open_count"] == 1

    audit_lines = (client_dir / "logs" / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(audit_lines) == 1
    audit = json.loads(audit_lines[0])
    assert audit["event"] == "incident_registered"
    assert audit["details"]["incident_id"] == result["incident_id"]


def test_incident_registration_blocks_without_confirmation_or_with_sensitive_values(tmp_path: Path):
    client_dir = tmp_path / "cliente_incident"
    write_incident_client(client_dir)

    missing_confirmation = run_incident(
        client_dir,
        incident_type="invalid_files",
        severity="media",
        responsible="Responsable Operativo",
        action_taken="Se pidio correccion de archivos.",
    )

    assert missing_confirmation["status"] == "sensitive_values_confirmation_required"

    sensitive_value = run_incident(
        client_dir,
        incident_type="accidental_sensitive_submission",
        severity="alta",
        responsible="Responsable Operativo",
        action_taken="Se pidio reenvio anonimizado.",
        notes="El cliente envio persona@example.com por error.",
        confirm_no_sensitive_values=True,
    )

    assert sensitive_value["status"] == "sensitive_value_detected"
    assert not list((client_dir / "diagnostics" / "incidents").glob("incident_*.json"))


def test_status_reports_blocking_open_incident_as_next_action(tmp_path: Path):
    client_dir = tmp_path / "cliente_incident"
    write_incident_client(client_dir)

    run_incident(
        client_dir,
        incident_type="invalid_files",
        severity="media",
        responsible="Responsable Operativo",
        action_taken="Se pidio correccion de archivos.",
        confirm_no_sensitive_values=True,
    )
    status = run_status(client_dir)

    assert status["incidents"]["open_count"] == 1
    assert status["incidents"]["blocking_open_count"] == 1
    assert status["next_action"] == "Resolver incidentes abiertos antes de continuar el flujo del cliente."


def test_readiness_blocks_when_blocking_incident_is_open(tmp_path: Path):
    client_dir = tmp_path / "cliente_incident_ready"
    write_valid_client(client_dir)
    ensure_operational_dirs(client_dir)
    assert run_preflight(client_dir)["status"] == "ready_for_analysis"

    run_incident(
        client_dir,
        incident_type="post_preflight_change",
        severity="media",
        responsible="Responsable Operativo",
        action_taken="Se descarto el preflight anterior y se pidio nueva verificacion.",
        confirm_no_sensitive_values=True,
    )
    readiness = run_readiness(client_dir, repo_root=None)

    assert readiness["can_continue"] is False
    assert "blocking_incidents_open" in {check["id"] for check in readiness["checks"]}


def test_resolve_incident_closes_record_and_unblocks_readiness(tmp_path: Path):
    client_dir = tmp_path / "cliente_incident_resolve"
    write_valid_client(client_dir)
    ensure_operational_dirs(client_dir)
    assert run_preflight(client_dir)["status"] == "ready_for_analysis"

    incident = run_incident(
        client_dir,
        incident_type="post_preflight_change",
        severity="media",
        responsible="Responsable Operativo",
        action_taken="Se descarto el preflight anterior.",
        confirm_no_sensitive_values=True,
    )
    assert run_readiness(client_dir, repo_root=None)["can_continue"] is False

    resolved = run_resolve_incident(
        client_dir,
        incident_id=incident["incident_id"],
        responsible="Responsable Operativo",
        resolution="Se ejecuto un nuevo control operativo sin registrar valores sensibles.",
        confirm_no_sensitive_values=True,
    )
    readiness = run_readiness(client_dir, repo_root=None)
    record = json.loads(Path(resolved["incident_record"]).read_text(encoding="utf-8"))
    audit_lines = (client_dir / "logs" / "audit.jsonl").read_text(encoding="utf-8").splitlines()

    assert resolved["status"] == "incident_resolved"
    assert record["incident_status"] == "closed"
    assert readiness["can_continue"] is True
    assert readiness["current_stage"] == "ready_for_analysis"
    assert [json.loads(line)["event"] for line in audit_lines][-2:] == ["incident_registered", "incident_resolved"]
