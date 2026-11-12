def test_unexpected_fault(ws):
    p = ws.CreatePolicy(holder="王小明", age=81, days=5)
    assert p.Status == "active"


def test_wrong_field_name(ws, policy):
    assert policy.Holder == "王小明"
    assert policy.HolderName == "王小明"
