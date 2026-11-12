from datetime import datetime

import pytest
from zeep.helpers import serialize_object


@pytest.mark.smoke
def test_create_policy(ws):
    p = ws.CreatePolicy(holder="林小美", age=30, days=5)

    assert p.PolicyNo.startswith("TP")
    assert p.Holder == "林小美"
    assert p.Premium == 150
    assert p.Status == "active"
    assert isinstance(p.CreatedAt, datetime)          # xsd:dateTime → datetime

    ws.CancelPolicy(policyNo=p.PolicyNo)              # 清理（其他測試改用 fixture）


def test_created_policy_can_be_read(ws, policy):
    found = ws.GetPolicy(policyNo=policy.PolicyNo)

    assert serialize_object(found, dict) == serialize_object(policy, dict)


def test_search_by_holder(ws, policy):
    found = ws.SearchPolicies(holder="王小明")

    assert policy.PolicyNo in [p.PolicyNo for p in found]
    assert all(p.Holder == "王小明" for p in found)


def test_search_no_result(ws):
    assert ws.SearchPolicies(holder="查無此人") is None      # 注意：不是空的 list


def test_cancel_policy(ws, policy):
    cancelled = ws.CancelPolicy(policyNo=policy.PolicyNo)
    assert cancelled.Status == "cancelled"

    assert ws.GetPolicy(policyNo=policy.PolicyNo).Status == "cancelled"
