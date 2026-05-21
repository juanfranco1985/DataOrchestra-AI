from __future__ import annotations

from pathlib import Path
from typing import Any
import re

import yaml


DEFAULT_THRESHOLDS: dict[str, float] = {
    "low_margin": 0.20,
    "critical_margin": 0.15,
    "excess_stock_ratio": 3.0,
    "revenue_concentration_top_n": 5,
    "revenue_concentration_warning": 0.50,
}


THRESHOLD_PROFILES: dict[str, dict[str, float]] = {
    "retail": {
        "low_margin": 0.22,
        "critical_margin": 0.14,
        "excess_stock_ratio": 3.0,
        "revenue_concentration_top_n": 5,
        "revenue_concentration_warning": 0.55,
    },
    "gastronomia": {
        "low_margin": 0.35,
        "critical_margin": 0.25,
        "excess_stock_ratio": 2.0,
        "revenue_concentration_top_n": 8,
        "revenue_concentration_warning": 0.45,
    },
    "distribucion": {
        "low_margin": 0.12,
        "critical_margin": 0.08,
        "excess_stock_ratio": 2.5,
        "revenue_concentration_top_n": 10,
        "revenue_concentration_warning": 0.60,
    },
    "ecommerce": {
        "low_margin": 0.25,
        "critical_margin": 0.16,
        "excess_stock_ratio": 2.5,
        "revenue_concentration_top_n": 8,
        "revenue_concentration_warning": 0.50,
    },
    "servicios": {
        "low_margin": 0.30,
        "critical_margin": 0.20,
        "excess_stock_ratio": 4.0,
        "revenue_concentration_top_n": 10,
        "revenue_concentration_warning": 0.65,
    },
}


PROFILE_ALIASES = {
    "comercio": "retail",
    "comercio_minorista": "retail",
    "minorista": "retail",
    "retail": "retail",
    "restaurant": "gastronomia",
    "restaurante": "gastronomia",
    "gastronomia": "gastronomia",
    "gastronomico": "gastronomia",
    "distribucion": "distribucion",
    "distribuidora": "distribucion",
    "mayorista": "distribucion",
    "ecommerce": "ecommerce",
    "e_commerce": "ecommerce",
    "online": "ecommerce",
    "servicio": "servicios",
    "servicios": "servicios",
}


def resolve_thresholds(client_dir: str | Path, runtime_overrides: dict[str, float] | None = None) -> dict[str, Any]:
    client_path = Path(client_dir)
    config = _read_client_config(client_path)
    analytics_config = config.get("analytics", {}) if isinstance(config.get("analytics"), dict) else {}
    business_type = str(config.get("client", {}).get("business_type") or "").strip()
    configured_profile = str(analytics_config.get("threshold_profile") or "").strip()
    configured_profile_is_auto = _normalize_key(configured_profile) in {"", "auto", "pendiente"}
    profile = _resolve_profile(business_type if configured_profile_is_auto else configured_profile)

    thresholds = dict(DEFAULT_THRESHOLDS)
    sources = ["default"]
    if profile in THRESHOLD_PROFILES:
        thresholds.update(THRESHOLD_PROFILES[profile])
        sources.append(f"profile:{profile}")

    client_overrides, ignored_client = _valid_threshold_overrides(analytics_config.get("thresholds", {}))
    if client_overrides:
        thresholds.update(client_overrides)
        sources.append("client_config")

    runtime_valid, ignored_runtime = _valid_threshold_overrides(runtime_overrides or {})
    if runtime_valid:
        thresholds.update(runtime_valid)
        sources.append("runtime_override")

    thresholds["revenue_concentration_top_n"] = int(thresholds["revenue_concentration_top_n"])
    profile_source = "client_config" if not configured_profile_is_auto else "business_type" if business_type and profile != "default" else "default"
    return {
        "business_type": business_type or None,
        "profile": profile,
        "profile_source": profile_source,
        "sources": sources,
        "thresholds": thresholds,
        "ignored_overrides": {**ignored_client, **ignored_runtime},
        "available_profiles": sorted(THRESHOLD_PROFILES),
    }


def _resolve_profile(value: str) -> str:
    normalized = _normalize_key(value)
    if normalized in {"", "auto", "pendiente"}:
        return "default"
    return PROFILE_ALIASES.get(normalized, normalized if normalized in THRESHOLD_PROFILES else "default")


def _valid_threshold_overrides(value: Any) -> tuple[dict[str, float], dict[str, Any]]:
    if not isinstance(value, dict):
        return {}, {}

    valid: dict[str, float] = {}
    ignored: dict[str, Any] = {}
    for key, raw in value.items():
        normalized_key = str(key)
        if normalized_key not in DEFAULT_THRESHOLDS:
            ignored[normalized_key] = raw
            continue
        try:
            number = float(raw)
        except (TypeError, ValueError):
            ignored[normalized_key] = raw
            continue
        if number < 0:
            ignored[normalized_key] = raw
            continue
        valid[normalized_key] = int(number) if normalized_key == "revenue_concentration_top_n" else number
    return valid, ignored


def _read_client_config(client_path: Path) -> dict[str, Any]:
    path = client_path / "client.yaml"
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _normalize_key(value: str) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^\w]+", "_", text, flags=re.UNICODE)
    return text.strip("_")
