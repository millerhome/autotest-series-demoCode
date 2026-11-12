"""練習用的保單 API：只用 Python 標準函式庫，資料放在記憶體。"""
import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from premium import calc_premium

USERS = {"tester": "test-pass-123"}      # 練習用的測試帳號
TOKENS = set()
POLICIES = {}
LOCK = threading.Lock()
SEQ = [0]


class ApiError(Exception):
    def __init__(self, status, message, field=None):
        self.status, self.message, self.field = status, message, field


def create_policy(body):
    for name in ("holder", "age", "days"):
        if name not in body:
            raise ApiError(422, f"缺少欄位：{name}", name)
    if not isinstance(body["holder"], str) or not body["holder"].strip():
        raise ApiError(422, "要保人姓名不可空白", "holder")
    for name in ("age", "days"):
        if not isinstance(body[name], int) or isinstance(body[name], bool):
            raise ApiError(422, f"{name} 必須是整數", name)
    try:
        premium = calc_premium(body["age"], body["days"])
    except ValueError as e:
        field = "age" if "年齡" in str(e) else "days"
        raise ApiError(422, str(e), field)
    with LOCK:
        SEQ[0] += 1
        no = f"TP{SEQ[0]:06d}"
        POLICIES[no] = {
            "no": no, "holder": body["holder"], "age": body["age"], "days": body["days"],
            "premium": premium, "currency": "TWD", "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    return POLICIES[no]


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status, body=None, headers=None):
        data = b"" if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        if body is not None:
            self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _json_body(self):
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        try:
            body = json.loads(raw.decode("utf-8"))
        except ValueError:
            raise ApiError(400, "JSON 格式錯誤")
        if not isinstance(body, dict):
            raise ApiError(400, "JSON 最外層必須是物件")
        return body

    def _require_token(self):
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or auth[7:] not in TOKENS:
            raise ApiError(401, "尚未登入或 token 無效")

    def _route(self, method):
        url = urlparse(self.path)
        path, q = url.path.rstrip("/"), parse_qs(url.query)
        allowed = None

        if path == "/api/health":
            allowed = "GET"
            if method == "GET":
                return self._send(200, {"status": "ok", "version": os.environ.get("APP_VERSION", "2.3.0")})
        elif path == "/api/quote":
            allowed = "GET"
            if method == "GET":
                try:
                    age, days = int(q["age"][0]), int(q["days"][0])
                except (KeyError, ValueError):
                    raise ApiError(422, "age 與 days 必須是整數")
                try:
                    premium = calc_premium(age, days)
                except ValueError as e:
                    raise ApiError(422, str(e), "age" if "年齡" in str(e) else "days")
                if os.environ.get("SERVICE_BUG") == "senior" and age >= 65:      # 練習用：故意放進去的缺陷
                    premium -= 5
                return self._send(200, {"premium": premium, "currency": "TWD"})
        elif path == "/api/slow":
            allowed = "GET"
            if method == "GET":
                time.sleep(float(q.get("seconds", ["2"])[0]))
                return self._send(200, {"status": "ok"})
        elif path == "/api/login":
            allowed = "POST"
            if method == "POST":
                body = self._json_body()
                if USERS.get(body.get("username")) != body.get("password"):
                    raise ApiError(401, "帳號或密碼錯誤")
                token = uuid.uuid4().hex
                TOKENS.add(token)
                return self._send(200, {"token": token, "token_type": "Bearer"})
        elif path == "/api/policies":
            allowed = "GET, POST"
            if method == "GET":
                self._require_token()
                holder = q.get("holder", [None])[0]
                items = [p for p in POLICIES.values() if holder in (None, p["holder"])]
                return self._send(200, {"items": items, "total": len(items)})
            if method == "POST":
                self._require_token()
                policy = create_policy(self._json_body())
                return self._send(201, policy, {"Location": f"/api/policies/{policy['no']}"})
        elif path.startswith("/api/policies/"):
            allowed = "GET, DELETE"
            no = path.rsplit("/", 1)[1]
            if method in ("GET", "DELETE"):
                self._require_token()
                if no not in POLICIES:
                    raise ApiError(404, f"找不到保單：{no}")
                if method == "GET":
                    return self._send(200, POLICIES[no])
                with LOCK:
                    del POLICIES[no]
                return self._send(204)
        if allowed:
            return self._send(405, {"error": "不支援這個方法"}, {"Allow": allowed})
        raise ApiError(404, "找不到這個路徑")

    def _handle(self, method):
        time.sleep(float(os.environ.get("API_DELAY", "0")))      # 模擬真實系統的回應時間
        try:
            self._route(method)
        except ApiError as e:
            body = {"error": e.message}
            if e.field:
                body["field"] = e.field
            headers = {"WWW-Authenticate": "Bearer"} if e.status == 401 else None
            self._send(e.status, body, headers)

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def do_PUT(self):
        self._handle("PUT")

    def do_DELETE(self):
        self._handle("DELETE")

    def log_message(self, *args):
        pass


def make_server(port=0):
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"保單 API 啟動：http://127.0.0.1:{port}")
    make_server(port).serve_forever()
