"""不靠 zeep，直接用 requests 送出 SOAP 信封：了解底層長什麼樣子。"""
import xml.etree.ElementTree as ET

import pytest
import requests

NS = {"soap": "http://schemas.xmlsoap.org/soap/envelope/",
      "p": "http://example.test/policy/"}

ENVELOPE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetQuote xmlns="http://example.test/policy/">
      {body}
    </GetQuote>
  </soap:Body>
</soap:Envelope>"""


def post_soap(ws_url, xml, action="GetQuote"):
    headers = {"Content-Type": "text/xml; charset=utf-8",
               "SOAPAction": f"http://example.test/policy/{action}"}
    return requests.post(ws_url, data=xml.encode("utf-8"), headers=headers, timeout=10)


@pytest.mark.smoke
def test_raw_quote(ws_url):
    r = post_soap(ws_url, ENVELOPE.format(body="<age>30</age><days>5</days>"))

    assert r.status_code == 200
    assert r.headers["Content-Type"].startswith("text/xml")
    root = ET.fromstring(r.content)
    assert root.findtext(".//p:Premium", namespaces=NS) == "150.00"
    assert root.findtext(".//p:Currency", namespaces=NS) == "TWD"


def test_raw_missing_age(ws_url):
    r = post_soap(ws_url, ENVELOPE.format(body="<days>5</days>"))

    assert r.status_code == 500                      # SOAP 1.1：Fault 一律是 500
    root = ET.fromstring(r.content)
    assert root.findtext(".//faultcode") == "soap:Client"
    assert root.findtext(".//faultstring") == "缺少欄位：age"


def test_raw_broken_xml(ws_url):
    r = post_soap(ws_url, "<soap:Envelope><oops>")

    assert r.status_code == 500
    assert ET.fromstring(r.content).findtext(".//faultstring") == "XML 格式錯誤"
