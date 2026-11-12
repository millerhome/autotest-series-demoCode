import pytest
from zeep.exceptions import Fault


@pytest.mark.regression
def test_policy_lifecycle(ws):
    # 1. 先試算
    quoted = ws.GetQuote(age=70, days=10).Premium

    # 2. 投保，保費要跟試算一致
    p = ws.CreatePolicy(holder="陳小華", age=70, days=10)
    assert p.Premium == quoted
    assert p.Status == "active"

    # 3. 查得到，也搜尋得到
    assert ws.GetPolicy(policyNo=p.PolicyNo).Holder == "陳小華"
    assert p.PolicyNo in [x.PolicyNo for x in ws.SearchPolicies(holder="陳小華")]

    # 4. 註銷
    assert ws.CancelPolicy(policyNo=p.PolicyNo).Status == "cancelled"

    # 5. 不能再註銷第二次
    with pytest.raises(Fault, match="保單已經註銷"):
        ws.CancelPolicy(policyNo=p.PolicyNo)
