from pathlib import Path

from dataorchestra.cli import run_thresholds
from dataorchestra.thresholds import resolve_thresholds


def test_thresholds_use_business_type_profile_alias(tmp_path: Path):
    client_dir = tmp_path / "cliente_thresholds"
    client_dir.mkdir()
    (client_dir / "client.yaml").write_text(
        "client:\n"
        "  id: cliente_thresholds\n"
        "  business_type: Comercio minorista\n",
        encoding="utf-8",
    )

    result = resolve_thresholds(client_dir)

    assert result["profile"] == "retail"
    assert result["profile_source"] == "business_type"
    assert result["thresholds"]["low_margin"] == 0.22
    assert "profile:retail" in result["sources"]


def test_thresholds_auto_profile_uses_business_type(tmp_path: Path):
    client_dir = tmp_path / "cliente_thresholds"
    client_dir.mkdir()
    (client_dir / "client.yaml").write_text(
        "client:\n"
        "  id: cliente_thresholds\n"
        "  business_type: Ecommerce\n"
        "analytics:\n"
        "  threshold_profile: auto\n",
        encoding="utf-8",
    )

    result = resolve_thresholds(client_dir)

    assert result["profile"] == "ecommerce"
    assert result["profile_source"] == "business_type"


def test_thresholds_allow_client_overrides_and_ignore_invalid_values(tmp_path: Path):
    client_dir = tmp_path / "cliente_thresholds"
    client_dir.mkdir()
    (client_dir / "client.yaml").write_text(
        "client:\n"
        "  id: cliente_thresholds\n"
        "  business_type: Retail\n"
        "analytics:\n"
        "  threshold_profile: distribucion\n"
        "  thresholds:\n"
        "    low_margin: 0.10\n"
        "    revenue_concentration_top_n: 12\n"
        "    unknown_threshold: 99\n"
        "    critical_margin: invalido\n",
        encoding="utf-8",
    )

    result = resolve_thresholds(client_dir)

    assert result["profile"] == "distribucion"
    assert result["profile_source"] == "client_config"
    assert result["thresholds"]["low_margin"] == 0.10
    assert result["thresholds"]["critical_margin"] == 0.08
    assert result["thresholds"]["revenue_concentration_top_n"] == 12
    assert result["ignored_overrides"]["unknown_threshold"] == 99
    assert result["ignored_overrides"]["critical_margin"] == "invalido"


def test_thresholds_cli_reports_active_configuration(tmp_path: Path):
    client_dir = tmp_path / "cliente_thresholds"
    client_dir.mkdir()
    (client_dir / "client.yaml").write_text(
        "client:\n"
        "  id: cliente_thresholds\n"
        "  business_type: Ecommerce\n",
        encoding="utf-8",
    )

    result = run_thresholds(client_dir)

    assert result["status"] == "thresholds_resolved"
    assert result["profile"] == "ecommerce"
    assert result["thresholds"]["excess_stock_ratio"] == 2.5
