from decimal import Decimal

import pytest


@pytest.mark.smoke
def test_quote_adult(ws):
    quote = ws.GetQuote(age=30, days=5)

    assert quote.Premium == 150
    assert quote.Currency == "TWD"


def test_quote_types(ws):
    quote = ws.GetQuote(age=30, days=5)

    assert isinstance(quote.Premium, Decimal)        # xsd:decimal → Decimal
    assert quote.Premium == Decimal("150.00")


@pytest.mark.parametrize("age, expected", [
    pytest.param(0, 120, id="0歲-承保下限"),
    pytest.param(17, 120, id="17歲-未成年上限"),
    pytest.param(18, 150, id="18歲-成年下限"),
    pytest.param(64, 150, id="64歲-成年上限"),
    pytest.param(65, 225, id="65歲-高齡下限"),
    pytest.param(80, 225, id="80歲-承保上限"),
])
def test_quote_age_bands(ws, age, expected):
    assert ws.GetQuote(age=age, days=5).Premium == expected
