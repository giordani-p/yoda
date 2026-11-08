"""Garante que a API implementada corresponde ao contrato em contracts/openapi/openapi.yaml.

Compara rotas, métodos, status codes, operationId e, nos schemas, nomes de propriedades e
campos obrigatórios. Tipos e validações não são comparados.
"""

from pathlib import Path
from typing import Any

import yaml

from app.main import app

CONTRACT = Path(__file__).resolve().parents[3] / "contracts" / "openapi" / "openapi.yaml"
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def _operations(spec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        f"{method.upper()} {path}": {
            "operationId": operation.get("operationId"),
            "responses": sorted(operation.get("responses", {})),
        }
        for path, item in spec.get("paths", {}).items()
        for method, operation in item.items()
        if method in HTTP_METHODS
    }


def _schemas(spec: dict[str, Any]) -> dict[str, dict[str, list[str]]]:
    return {
        name: {
            "properties": sorted(schema.get("properties", {})),
            "required": sorted(schema.get("required", [])),
        }
        for name, schema in spec.get("components", {}).get("schemas", {}).items()
    }


def test_operations_match_contract() -> None:
    contract = yaml.safe_load(CONTRACT.read_text())
    assert _operations(app.openapi()) == _operations(contract)


def test_schemas_match_contract() -> None:
    contract = yaml.safe_load(CONTRACT.read_text())
    assert _schemas(app.openapi()) == _schemas(contract)
