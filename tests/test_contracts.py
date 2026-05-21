import csv
import json
from pathlib import Path

from dataorchestra.cli import run_data_contracts
from dataorchestra.contracts import DATA_CONTRACT_VERSION, export_contracts_payload, expected_files, validation_schema
from dataorchestra.validation import validate_client_raw


def test_contract_json_artifact_matches_runtime_contracts():
    artifact = json.loads(Path("contracts/data_contracts_v1.json").read_text(encoding="utf-8"))

    assert artifact == export_contracts_payload()


def test_templates_match_required_contract_headers():
    for dataset, file_name in expected_files().items():
        template_path = Path("templates") / file_name.replace(".csv", "_template.csv")
        with template_path.open("r", encoding="utf-8-sig", newline="") as handle:
            headers = set(csv.DictReader(handle).fieldnames or [])

        assert headers == validation_schema(dataset)["required"]


def test_validation_report_includes_contract_version(tmp_path: Path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    for file_name in expected_files().values():
        template = Path("templates") / file_name.replace(".csv", "_template.csv")
        (raw_dir / file_name).write_text(template.read_text(encoding="utf-8"), encoding="utf-8")

    report = validate_client_raw(raw_dir)

    assert report.contract_version == DATA_CONTRACT_VERSION
    assert report.to_dict()["contract_version"] == DATA_CONTRACT_VERSION
    assert report.can_continue is True


def test_data_contracts_cli_can_return_single_dataset():
    result = run_data_contracts(dataset="ventas")

    assert result["status"] == "data_contracts_ready"
    assert result["contract_version"] == DATA_CONTRACT_VERSION
    assert list(result["datasets"]) == ["ventas"]
