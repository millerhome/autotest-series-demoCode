import json
from pathlib import Path

import pytest
from jsonschema import ValidationError, validate

SCHEMA_DIR = Path(__file__).parent / "schemas"


def load_schema(name):
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


def test_policy_matches_schema(api, policy):
    r = api.get(f"/api/policies/{policy['no']}")
    assert r.status_code == 200
    validate(instance=r.json(), schema=load_schema("policy.json"))


def test_list_items_match_schema(api, policy):
    schema = load_schema("policy.json")
    for item in api.get("/api/policies").json()["items"]:
        validate(instance=item, schema=schema)


def test_schema_catches_wrong_type():
    bad = {"no": "TP000001", "holder": "王小明", "age": 30, "days": 5,
           "premium": "150", "currency": "TWD", "status": "active",
           "created_at": "2026-01-01T00:00:00+00:00"}
    with pytest.raises(ValidationError, match="is not of type 'integer'"):
        validate(instance=bad, schema=load_schema("policy.json"))
