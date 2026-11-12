"""練習用的保單 Web Service（SOAP 1.1）：只用 Python 標準函式庫，資料放在記憶體。"""
import os
import threading
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from xml.sax.saxutils import escape

from premium import calc_premium

NS = "http://example.test/policy/"
SOAP = "http://schemas.xmlsoap.org/soap/envelope/"
PATH = "/PolicyService.asmx"
WSDL = (Path(__file__).parent / "PolicyService.wsdl").read_text(encoding="utf-8")

USERS = {"tester": "test-pass-123"}      # 練習用的測試帳號
TOKENS = set()
POLICIES = {}
LOCK = threading.Lock()
SEQ = [0]
NEED_TOKEN = {"CreatePolicy", "GetPolicy", "SearchPolicies", "CancelPolicy"}


class SoapFault(Exception):
    def __init__(self, message, field=None, code="soap:Client"):
        self.message, self.field, self.code = message, field, code


def wsdl_text(location):
    text = WSDL.replace("__LOCATION__", location)
    if os.environ.get("WS_VARIANT") == "v2":        # 模擬「介面被改動」：課程第 7 章使用
        text = text.replace('<s:element name="Holder" type="s:string" minOccurs="0"/>',
                            '<s:element name="HolderName" type="s:string" minOccurs="0"/>')
        text = text.replace('<s:element name="Days" type="s:int"/>\n          <s:element name="Premium" type="s:decimal"/>',
                            '<s:element name="Days" type="s:int"/>\n          <s:element name="Premium" type="s:int"/>')
    return text


def text_of(req, name):
    node = req.find(f"{{{NS}}}{name}")
    return None if node is None else (node.text or "")


def int_of(req, name):
    value = text_of(req, name)
    if value is None:
        raise SoapFault(f"缺少欄位：{name}", name)
    try:
        return int(value)
    except ValueError:
        raise SoapFault(f"{name} 必須是整數", name)


def premium_of(age, days):
    try:
        return calc_premium(age, days)
    except ValueError as e:
        raise SoapFault(str(e), "age" if "年齡" in str(e) else "days")


def policy_xml(p, tag="Policy"):
    return (f"<{tag}><PolicyNo>{p['no']}</PolicyNo><Holder>{escape(p['holder'])}</Holder>"
            f"<Age>{p['age']}</Age><Days>{p['days']}</Days><Premium>{p['premium']:.2f}</Premium>"
            f"<Currency>TWD</Currency><Status>{p['status']}</Status>"
            f"<CreatedAt>{p['created_at']}</CreatedAt></{tag}>")


def find_policy(req):
    no = text_of(req, "policyNo") or ""
    if no not in POLICIES:
        raise SoapFault(f"找不到保單：{no}", "policyNo")
    return POLICIES[no]


def op_GetQuote(req):
    premium = premium_of(int_of(req, "age"), int_of(req, "days"))
    return f"<GetQuoteResult><Premium>{premium:.2f}</Premium><Currency>TWD</Currency></GetQuoteResult>"


def op_Login(req):
    user, pwd = text_of(req, "username"), text_of(req, "password")
    if USERS.get(user) != pwd:
        raise SoapFault("帳號或密碼錯誤")
    token = uuid.uuid4().hex
    TOKENS.add(token)
    return f"<LoginResult>{token}</LoginResult>"


def op_CreatePolicy(req):
    holder = text_of(req, "holder")
    if holder is None:
        raise SoapFault("缺少欄位：holder", "holder")
    if not holder.strip():
        raise SoapFault("要保人姓名不可空白", "holder")
    age, days = int_of(req, "age"), int_of(req, "days")
    premium = premium_of(age, days)
    with LOCK:
        SEQ[0] += 1
        no = f"TP{SEQ[0]:06d}"
        POLICIES[no] = {"no": no, "holder": holder, "age": age, "days": days,
                        "premium": premium, "status": "active",
                        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    return policy_xml(POLICIES[no], "CreatePolicyResult")


def op_GetPolicy(req):
    return policy_xml(find_policy(req), "GetPolicyResult")


def op_SearchPolicies(req):
    holder = text_of(req, "holder") or ""
    items = [p for p in POLICIES.values() if not holder or p["holder"] == holder]
    return "<SearchPoliciesResult>" + "".join(policy_xml(p) for p in items) + "</SearchPoliciesResult>"


def op_CancelPolicy(req):
    p = find_policy(req)
    if p["status"] == "cancelled":
        raise SoapFault(f"保單已經註銷：{p['no']}", "policyNo")
    p["status"] = "cancelled"
    return policy_xml(p, "CancelPolicyResult")


def envelope(inner):
    return ('<?xml version="1.0" encoding="utf-8"?>'
            f'<soap:Envelope xmlns:soap="{SOAP}"><soap:Body>{inner}</soap:Body></soap:Envelope>')


def handle(raw):
    """回傳 (HTTP 狀態碼, 回應的 XML)。"""
    try:
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            raise SoapFault("XML 格式錯誤")
        body = root.find(f"{{{SOAP}}}Body")
        if body is None or len(body) == 0:
            raise SoapFault("找不到 soap:Body")
        req = body[0]
        name = req.tag.replace(f"{{{NS}}}", "")
        op = globals().get(f"op_{name}")
        if op is None or not req.tag.startswith(f"{{{NS}}}"):
            raise SoapFault(f"不支援的操作：{name}")
        if name in NEED_TOKEN:
            token = root.find(f"{{{SOAP}}}Header/{{{NS}}}AuthHeader/{{{NS}}}Token")
            if token is None or token.text not in TOKENS:
                raise SoapFault("尚未登入或 Token 無效")
        return 200, envelope(f'<{name}Response xmlns="{NS}">{op(req)}</{name}Response>')
    except SoapFault as e:
        detail = (f'<detail><ValidationError xmlns="{NS}"><Field>{e.field}</Field></ValidationError></detail>'
                  if e.field else "")
        return 500, envelope(f"<soap:Fault><faultcode>{e.code}</faultcode>"
                             f"<faultstring>{escape(e.message)}</faultstring>{detail}</soap:Fault>")
    except Exception as e:                                  # 沒預期到的錯誤
        return 500, envelope("<soap:Fault><faultcode>soap:Server</faultcode>"
                             f"<faultstring>{escape(str(e))}</faultstring></soap:Fault>")


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status, text, ctype="text/xml; charset=utf-8"):
        data = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path, _, query = self.path.partition("?")
        if path == PATH and query.lower() == "wsdl":
            host = self.headers.get("Host", "127.0.0.1")
            self._send(200, wsdl_text(f"http://{host}{PATH}"))
        elif path == PATH:
            self._send(200, "PolicyService：請用 ?WSDL 取得服務描述", "text/plain; charset=utf-8")
        else:
            self._send(404, "找不到這個路徑", "text/plain; charset=utf-8")

    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if self.path.partition("?")[0] != PATH:
            self._send(404, "找不到這個路徑", "text/plain; charset=utf-8")
            return
        self._send(*handle(raw))

    def log_message(self, *args):
        pass


def make_server(port=0):
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    server = make_server(8000)
    print(f"保單 Web Service 啟動：http://127.0.0.1:8000{PATH}?WSDL")
    server.serve_forever()
