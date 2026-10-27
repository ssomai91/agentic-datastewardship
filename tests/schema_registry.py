"""Load every schema under schemas/ into one registry so $ref between schemas resolves offline."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def all_schema_paths():
    return sorted(SCHEMAS.rglob("*.schema.json"))


def build_registry():
    resources = []
    for path in all_schema_paths():
        schema = load(path)
        resources.append((schema["$id"], Resource.from_contents(schema, default_specification=DRAFT202012)))
    return Registry().with_resources(resources)


REGISTRY = build_registry()


def validator_for(path):
    return Draft202012Validator(load(path), registry=REGISTRY)