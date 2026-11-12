from jsonschema import validate


def test_plain_assert(api):
    r = api.post("/api/policies", json={"holder": "王小明", "age": 81, "days": 5})
    assert r.status_code == 201


def test_assert_with_body(api):
    r = api.post("/api/policies", json={"holder": "王小明", "age": 81, "days": 5})
    assert r.status_code == 201, f"{r.status_code} {r.text}"


def test_json_on_empty_body(api, policy):
    r = api.delete(f"/api/policies/{policy['no']}")
    assert r.json() == {}


def test_schema_mismatch(api, policy):
    schema = {
        "type": "object",
        "required": ["no", "holder", "premium", "agent_code"],
        "properties": {"premium": {"type": "integer"}},
    }
    validate(instance=policy, schema=schema)
