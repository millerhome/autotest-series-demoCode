"""練習用的報價服務：一個 API 加一個網頁，只用 Python 標準函式庫。"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from premium import calc_premium

PAGE = """<!doctype html><html lang="zh-Hant"><meta charset="utf-8">
<title>旅平險試算</title>
<h1>旅平險試算</h1>
<label>年齡 <input id="age" type="number"></label>
<label>天數 <input id="days" type="number"></label>
<button id="go">試算</button>
<p role="status" id="result"></p>
<script>
document.getElementById("go").onclick = async () => {
  const q = `age=${age.value}&days=${days.value}`;
  const r = await fetch("/api/quote?" + q);
  const d = await r.json();
  result.textContent = r.ok ? `保費 ${d.premium} 元` : `錯誤：${d.error}`;
};
</script></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, status, body, ctype):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            return self._send(200, PAGE, "text/html")
        if url.path == "/api/quote":
            q = parse_qs(url.query)
            try:
                premium = calc_premium(int(q["age"][0]), int(q["days"][0]))
            except (KeyError, ValueError) as e:
                return self._send(422, json.dumps({"error": str(e)}, ensure_ascii=False), "application/json")
            return self._send(200, json.dumps({"premium": premium, "currency": "TWD"}), "application/json")
        self._send(404, json.dumps({"error": "not found"}), "application/json")

    def log_message(self, *args):
        pass


def make_server(port: int = 0) -> ThreadingHTTPServer:
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    server = make_server(8000)
    print("http://127.0.0.1:8000")
    server.serve_forever()
