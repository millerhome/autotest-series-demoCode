import pytest
from zeep.exceptions import Fault, ValidationError

NS = "http://example.test/policy/"


def fault_field(fault):
    """從 Fault 的 detail 取出有問題的欄位名稱。"""
    return fault.detail.findtext(f".//{{{NS}}}Field")


@pytest.mark.parametrize("args, message, field", [
    pytest.param({"holder": "", "age": 30, "days": 5}, "要保人姓名不可空白", "holder", id="holder空白"),
    pytest.param({"age": 30, "days": 5}, "缺少欄位：holder", "holder", id="缺少holder"),
    pytest.param({"holder": "王小明", "age": 81, "days": 5}, "年齡不在承保範圍", "age", id="超過承保上限"),
    pytest.param({"holder": "王小明", "age": 30, "days": 0}, "天數至少 1 天", "days", id="天數為零"),
])
def test_create_policy_faults(ws, args, message, field):
    before = len(ws.SearchPolicies(holder="王小明") or [])

    with pytest.raises(Fault) as excinfo:
        ws.CreatePolicy(**args)

    fault = excinfo.value
    assert fault.code == "soap:Client"
    assert fault.message == message
    assert fault_field(fault) == field
    assert len(ws.SearchPolicies(holder="王小明") or []) == before     # 沒有多出資料


def test_policy_not_found(ws):
    with pytest.raises(Fault, match="找不到保單：TP999999"):
        ws.GetPolicy(policyNo="TP999999")


def test_cancel_twice(ws, policy):
    ws.CancelPolicy(policyNo=policy.PolicyNo)

    with pytest.raises(Fault, match="保單已經註銷"):
        ws.CancelPolicy(policyNo=policy.PolicyNo)


def test_requires_login(anon):
    with pytest.raises(Fault, match="尚未登入或 Token 無效"):
        anon.SearchPolicies(holder="王小明")


def test_login_wrong_password(anon):
    with pytest.raises(Fault, match="帳號或密碼錯誤"):
        anon.Login(username="tester", password="wrong")


def test_zeep_checks_before_sending(ws):
    # age 在 WSDL 裡是必填：zeep 在送出之前就會擋下來，請求根本沒有送到服務
    with pytest.raises(ValidationError, match="Missing element age"):
        ws.GetQuote(days=5)
