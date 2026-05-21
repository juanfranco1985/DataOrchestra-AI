from __future__ import annotations

from copy import deepcopy
from typing import Any


DATA_CONTRACT_VERSION = "1.0"
REQUIRED_DATASETS = ("ventas", "productos", "stock")


DATA_CONTRACTS: dict[str, dict[str, Any]] = {
    "ventas": {
        "dataset": "ventas",
        "file_name": "ventas.csv",
        "description": "Operaciones comerciales anonimizadas usadas para calcular ventas, margen, volumen y periodo.",
        "pii_allowed": False,
        "minimum_rows": 1,
        "columns": {
            "fecha": {
                "type": "date_iso",
                "required": True,
                "rules": ["format:YYYY-MM-DD", "not_empty"],
                "example": "2026-01-01",
                "description": "Fecha de la operacion en formato ISO.",
            },
            "producto": {
                "type": "string",
                "required": True,
                "rules": ["not_empty", "anonymized_business_label"],
                "example": "Producto A",
                "description": "Nombre o codigo anonimo del producto vendido.",
            },
            "categoria": {
                "type": "string",
                "required": True,
                "rules": ["not_empty", "anonymized_business_label"],
                "example": "Categoria 1",
                "description": "Categoria comercial anonima del producto.",
            },
            "cantidad": {
                "type": "number",
                "required": True,
                "rules": ["not_empty", "non_negative"],
                "example": 1,
                "description": "Unidades vendidas en la operacion.",
            },
            "precio_unitario": {
                "type": "money",
                "required": True,
                "rules": ["not_empty", "non_negative"],
                "example": 1000,
                "description": "Precio unitario de venta.",
            },
            "costo_unitario": {
                "type": "money",
                "required": True,
                "rules": ["not_empty", "non_negative"],
                "example": 700,
                "description": "Costo unitario usado para estimar margen.",
            },
        },
    },
    "productos": {
        "dataset": "productos",
        "file_name": "productos.csv",
        "description": "Catalogo comercial anonimizado usado para contrastar categorias, precios y costos.",
        "pii_allowed": False,
        "minimum_rows": 1,
        "columns": {
            "producto": {
                "type": "string",
                "required": True,
                "rules": ["not_empty", "anonymized_business_label"],
                "example": "Producto A",
                "description": "Nombre o codigo anonimo del producto.",
            },
            "categoria": {
                "type": "string",
                "required": True,
                "rules": ["not_empty", "anonymized_business_label"],
                "example": "Categoria 1",
                "description": "Categoria comercial anonima del producto.",
            },
            "precio_unitario": {
                "type": "money",
                "required": True,
                "rules": ["not_empty", "non_negative"],
                "example": 1000,
                "description": "Precio de referencia del producto.",
            },
            "costo_unitario": {
                "type": "money",
                "required": True,
                "rules": ["not_empty", "non_negative"],
                "example": 700,
                "description": "Costo unitario de referencia.",
            },
        },
    },
    "stock": {
        "dataset": "stock",
        "file_name": "stock.csv",
        "description": "Existencias y rotacion reciente usadas para detectar stock bajo o capital inmovilizado.",
        "pii_allowed": False,
        "minimum_rows": 1,
        "columns": {
            "producto": {
                "type": "string",
                "required": True,
                "rules": ["not_empty", "anonymized_business_label"],
                "example": "Producto A",
                "description": "Nombre o codigo anonimo del producto.",
            },
            "stock_actual": {
                "type": "number",
                "required": True,
                "rules": ["not_empty", "non_negative"],
                "example": 20,
                "description": "Existencias actuales disponibles.",
            },
            "stock_minimo": {
                "type": "number",
                "required": True,
                "rules": ["not_empty", "non_negative"],
                "example": 5,
                "description": "Nivel minimo operativo informado por el cliente.",
            },
            "ventas_ultimos_30_dias": {
                "type": "number",
                "required": True,
                "rules": ["not_empty", "non_negative"],
                "example": 12,
                "description": "Ventas o salidas del producto durante los ultimos 30 dias.",
            },
        },
    },
}


def export_contracts_payload(dataset: str | None = None) -> dict[str, Any]:
    if dataset:
        return {
            "contract_version": DATA_CONTRACT_VERSION,
            "datasets": {dataset: deepcopy(dataset_contract(dataset))},
        }
    return {
        "contract_version": DATA_CONTRACT_VERSION,
        "datasets": deepcopy(DATA_CONTRACTS),
    }


def dataset_contract(dataset: str) -> dict[str, Any]:
    if dataset not in DATA_CONTRACTS:
        raise KeyError(f"Unknown data contract dataset: {dataset}")
    return DATA_CONTRACTS[dataset]


def expected_files() -> dict[str, str]:
    return {dataset: DATA_CONTRACTS[dataset]["file_name"] for dataset in REQUIRED_DATASETS}


def validation_schema(dataset: str) -> dict[str, set[str]]:
    contract = dataset_contract(dataset)
    columns = contract["columns"]
    required = {name for name, spec in columns.items() if spec.get("required") is True}
    numeric_non_negative = {
        name
        for name, spec in columns.items()
        if spec.get("type") in {"number", "money"} and "non_negative" in spec.get("rules", [])
    }
    date = {name for name, spec in columns.items() if spec.get("type") == "date_iso"}
    return {
        "required": required,
        "numeric_non_negative": numeric_non_negative,
        "date": date,
    }


def dataset_for_file(file_name: str) -> str | None:
    normalized = str(file_name).strip().lower()
    for dataset, contract in DATA_CONTRACTS.items():
        if contract["file_name"] == normalized:
            return dataset
    return None
