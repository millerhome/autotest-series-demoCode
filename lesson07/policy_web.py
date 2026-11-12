"""練習用的保單網站：登入、保費試算、保單管理。只用 Python 標準函式庫，資料放在記憶體。"""
import json
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from premium import calc_premium

USERS = {"tester": "test-pass-123"}      # 練習用的測試帳號
SESSIONS = {}
POLICIES = {}
LOCK = threading.Lock()
SEQ = [0]
DELAY = 0.6                              # 故意延遲，模擬真實系統的回應時間

CSS = """
*{box-sizing:border-box} body{margin:0;font-family:"PingFang TC","Microsoft JhengHei",sans-serif;background:#f4f6fb;color:#27304a}
header{background:#3b4a8c;color:#fff;padding:10px 28px;display:flex;align-items:center;gap:28px}
header h1{font-size:20px;margin:0} nav a{color:#dfe5ff;margin-right:18px;text-decoration:none} nav a[aria-current]{color:#fff;font-weight:700;border-bottom:2px solid #fff}
header .user{margin-left:auto;font-size:14px} main{padding:18px 28px} h2{margin:0 0 12px;font-size:22px}
.card{background:#fff;border-radius:10px;padding:16px 20px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:14px}
label{font-size:14px;margin-right:6px} input,select{padding:6px 8px;border:1px solid #b9c0d8;border-radius:6px;font-size:15px;margin-right:14px}
input[type=number]{width:80px} button{padding:7px 16px;border:0;border-radius:6px;background:#3b4a8c;color:#fff;font-size:15px;cursor:pointer}
button.link{background:#fff;color:#b3261e;border:1px solid #b3261e;padding:3px 10px;font-size:13px} button:disabled{opacity:.5}
[role=status]{font-size:20px;font-weight:700;color:#1b7a3d;margin-top:10px;min-height:28px} [role=alert]{color:#b3261e;font-weight:700;margin-top:10px}
table{border-collapse:collapse;width:100%} th,td{border-bottom:1px solid #e1e5f0;padding:6px 10px;text-align:left;font-size:15px} th{background:#eef1fa}
caption{text-align:left;font-weight:700;margin-bottom:6px} .muted{color:#7a829c} .login{max-width:380px;margin:50px auto} .login label{display:block;margin:10px 0 4px} .login input{width:100%;margin:0}
.login button{margin-top:16px;width:100%}
"""


def page(title, body, user=None, current=""):
    def link(href, text):
        cur = ' aria-current="page"' if href == current else ""
        return f'<a href="{href}"{cur}>{text}</a>'
    nav = (f'<nav aria-label="主選單">{link("/quote", "保費試算")}{link("/policies", "保單管理")}</nav>'
           f'<span class="user">歡迎，{user}　<a href="/logout" style="color:#fff">登出</a></span>') if user else ""
    return (f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>{title}｜旅平險服務</title>'
            f'<style>{CSS}</style></head><body><header><h1>旅平險服務</h1>{nav}</header><main>{body}</main></body></html>')


LOGIN = """<div class="card login"><h2>登入</h2>
<form method="post" action="/login">
<label for="u">帳號</label><input id="u" name="username" autocomplete="off">
<label for="p">密碼</label><input id="p" name="password" type="password">
<button type="submit">登入</button></form>{error}</div>"""

QUOTE = """<h2>保費試算</h2><div class="card">
<label for="age">年齡</label><input id="age" type="number">
<label for="days">天數</label><input id="days" type="number">
<label for="plan">方案</label><select id="plan"><option value="basic">基本型</option><option value="plus">豪華型</option></select>
<label><input type="checkbox" id="addon" style="margin-right:4px">加購不便險</label>
<button id="go" type="button">試算</button>
<div role="status" aria-live="polite"></div><div role="alert"></div></div>
<p class="muted">豪華型為基本型的 1.5 倍；不便險每天加收 10 元。</p>
<script>
const $=id=>document.getElementById(id), st=document.querySelector('[role=status]'), al=document.querySelector('[role=alert]');
async function quote(){ st.textContent='計算中…'; al.textContent=''; $('go').disabled=true;
  const q=new URLSearchParams({age:$('age').value,days:$('days').value,plan:$('plan').value,addon:$('addon').checked?1:0});
  const r=await fetch('/api/quote?'+q); const d=await r.json(); $('go').disabled=false;
  if(r.ok){ st.textContent='保費 '+d.premium+' 元'; } else { st.textContent=''; al.textContent=d.error; } }
$('go').addEventListener('click',quote);
document.querySelectorAll('input[type=number]').forEach(e=>e.addEventListener('keydown',ev=>{if(ev.key==='Enter')quote()}));
</script>"""

POLICY = """<h2>保單管理</h2><div class="card">
<label for="holder">要保人</label><input id="holder" placeholder="請輸入姓名">
<label for="age">年齡</label><input id="age" type="number">
<label for="days">天數</label><input id="days" type="number">
<button id="add" type="button">新增保單</button><div role="alert"></div></div>
<div class="card"><label for="kw">搜尋</label><input id="kw" type="search" placeholder="輸入要保人姓名">
<span data-testid="policy-count" class="muted"></span>
<table><caption>保單清單</caption><thead><tr><th>保單號碼</th><th>要保人</th><th>年齡</th><th>天數</th><th>保費</th><th>狀態</th><th>操作</th></tr></thead>
<tbody></tbody></table><p id="empty" class="muted" hidden>目前沒有符合的保單</p></div>
<script>
const $=id=>document.getElementById(id), tb=document.querySelector('tbody'), al=document.querySelector('[role=alert]'); let items=[];
function render(){ const kw=$('kw').value.trim(); const rows=items.filter(p=>p.holder.includes(kw)); tb.innerHTML='';
  for(const p of rows){ const tr=document.createElement('tr');
    const s=p.status==='active'?'有效':'已註銷';
    tr.innerHTML=`<td>${p.no}</td><td>${p.holder}</td><td>${p.age}</td><td>${p.days}</td><td>${p.premium}</td><td>${s}</td><td></td>`;
    tr.children[1].textContent=p.holder;
    if(p.status==='active'){ const b=document.createElement('button'); b.className='link'; b.textContent='註銷'; b.setAttribute('aria-label','註銷 '+p.no);
      b.onclick=async()=>{ if(!confirm('確定要註銷保單 '+p.no+' 嗎？'))return; await fetch('/api/policies/'+p.no+'/cancel',{method:'POST'}); load(); };
      tr.children[6].appendChild(b); }
    tb.appendChild(tr); }
  $('empty').hidden=rows.length>0; document.querySelector('[data-testid=policy-count]').textContent='共 '+rows.length+' 筆'; }
async function load(){ const r=await fetch('/api/policies'); items=(await r.json()).items; render(); }
$('kw').addEventListener('input',render);
$('add').addEventListener('click',async()=>{ al.textContent=''; $('add').disabled=true;
  const r=await fetch('/api/policies',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({holder:$('holder').value,age:Number($('age').value),days:Number($('days').value)})});
  $('add').disabled=false; if(r.ok){ $('holder').value='';$('age').value='';$('days').value=''; load(); } else { al.textContent=(await r.json()).error; } });
load();
</script>"""


class ApiError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


def quote(age, days, plan="basic", addon=False):
    try:
        base = calc_premium(age, days)
    except ValueError as e:
        raise ApiError(422, str(e))
    return round(base * (1.5 if plan == "plus" else 1)) + (days * 10 if addon else 0)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, status, body, ctype="text/html; charset=utf-8", headers=None):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status, obj):
        self._send(status, json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

    def _user(self):
        for part in self.headers.get("Cookie", "").split(";"):
            k, _, v = part.strip().partition("=")
            if k == "sid":
                return SESSIONS.get(v)
        return None

    def _redirect(self, to, headers=None):
        self._send(303, "", headers={"Location": to, **(headers or {})})

    def _handle(self, method):
        url = urlparse(self.path)
        path, q = url.path, parse_qs(url.query)
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        user = self._user()
        try:
            if path == "/login" and method == "GET":
                return self._send(200, page("登入", LOGIN.format(error="")))
            if path == "/login" and method == "POST":
                form = parse_qs(raw.decode("utf-8"))
                name, pwd = form.get("username", [""])[0], form.get("password", [""])[0]
                if USERS.get(name) != pwd:
                    return self._send(200, page("登入", LOGIN.format(error='<div role="alert">帳號或密碼錯誤</div>')))
                sid = uuid.uuid4().hex
                SESSIONS[sid] = name
                return self._redirect("/quote", {"Set-Cookie": f"sid={sid}; Path=/; HttpOnly"})
            if path == "/logout":
                return self._redirect("/login", {"Set-Cookie": "sid=; Path=/; Max-Age=0"})
            if user is None:
                if path.startswith("/api/"):
                    raise ApiError(401, "尚未登入")
                return self._redirect("/login")
            if path == "/":
                return self._redirect("/quote")
            if path == "/quote":
                return self._send(200, page("保費試算", QUOTE, user, "/quote"))
            if path == "/policies":
                return self._send(200, page("保單管理", POLICY, user, "/policies"))
            if path == "/api/quote":
                time.sleep(DELAY)
                try:
                    age, days = int(q["age"][0]), int(q["days"][0])
                except (KeyError, ValueError):
                    raise ApiError(422, "年齡與天數必須是整數")
                premium = quote(age, days, q.get("plan", ["basic"])[0], q.get("addon", ["0"])[0] == "1")
                return self._json(200, {"premium": premium})
            if path == "/api/policies" and method == "GET":
                return self._json(200, {"items": list(POLICIES.values())})
            if path == "/api/policies" and method == "POST":
                time.sleep(DELAY)
                body = json.loads(raw.decode("utf-8"))
                if not str(body.get("holder", "")).strip():
                    raise ApiError(422, "要保人姓名不可空白")
                premium = quote(int(body.get("age") or 0), int(body.get("days") or 0))
                with LOCK:
                    SEQ[0] += 1
                    no = f"TP{SEQ[0]:06d}"
                    POLICIES[no] = {"no": no, "holder": body["holder"], "age": body["age"],
                                    "days": body["days"], "premium": premium, "status": "active"}
                return self._json(201, POLICIES[no])
            parts = path.strip("/").split("/")
            if method == "POST" and parts[:2] == ["api", "policies"] and parts[3:] == ["cancel"]:
                if parts[2] not in POLICIES:
                    raise ApiError(404, "找不到保單")
                POLICIES[parts[2]]["status"] = "cancelled"
                return self._json(200, POLICIES[parts[2]])
            if method == "POST" and path == "/api/test/reset":         # 只給練習用：清空保單
                POLICIES.clear()
                return self._json(200, {"ok": True})
            self._send(404, page("找不到頁面", "<h2>找不到頁面</h2>", user))
        except ApiError as e:
            self._json(e.status, {"error": e.message})

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def log_message(self, *args):
        pass


def make_server(port=0):
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    print("保單網站啟動：http://127.0.0.1:8000　帳號 tester")
    make_server(8000).serve_forever()
