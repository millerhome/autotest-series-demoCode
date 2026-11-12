"""練習用網站：用 Python 模擬 WebForms 與 Blazor 頁面「在瀏覽器裡的行為」。

這不是真正的 ASP.NET：只模擬測試會遇到的現象（自動產生的 id、postback、UpdatePanel 局部更新、
Blazor 的載入與互動時機），讓沒有 IIS 的電腦也能練習。實際行為請在公司的系統上驗證。
"""
import html
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from premium import calc_premium

DELAY = 0.5
P = os.environ.get("ID_PREFIX", "ctl00_MainContent_")     # 命名容器產生的 id 前綴；可用環境變數模擬「主版頁面改版」
REGIONS = {"asia": ("亞洲", 1.0, ["基本型", "豪華型"]),
           "europe": ("歐洲", 1.2, ["申根基本型", "申根豪華型"]),
           "america": ("美洲", 1.5, ["美加基本型", "美加豪華型"])}
SEED = [("王小明", 30, 5), ("林小美", 70, 10), ("陳小華", 10, 3), ("張大同", 45, 7),
        ("李美玲", 28, 14), ("吳志明", 66, 4), ("黃淑芬", 52, 9)]
POLICIES = []
LOCK = threading.Lock()


def reset():
    with LOCK:
        POLICIES.clear()
        for i, (holder, age, days) in enumerate(SEED, 1):
            POLICIES.append({"no": f"TP{i:06d}", "holder": holder, "age": age, "days": days,
                             "premium": calc_premium(age, days), "status": "有效"})


def add_policy(holder, age, days):
    with LOCK:
        no = f"TP{len(POLICIES) + 1:06d}"
        POLICIES.append({"no": no, "holder": holder, "age": age, "days": days,
                         "premium": calc_premium(age, days), "status": "有效"})
    return POLICIES[-1]


CSS = """*{box-sizing:border-box} body{margin:0;font-family:"PingFang TC","Microsoft JhengHei",sans-serif;background:#f4f6fb;color:#27304a}
#header{background:#5b3b8c;color:#fff;padding:10px 28px;display:flex;gap:26px;align-items:center} #header b{font-size:19px} #header a{color:#e6dcff;text-decoration:none}
#main{padding:16px 28px} h2{margin:0 0 12px;font-size:21px} .box{background:#fff;border-radius:10px;padding:14px 18px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:12px}
input[type=text],select{padding:5px 8px;border:1px solid #b9c0d8;border-radius:6px;font-size:15px;margin-right:14px} input[type=text].num{width:70px}
input[type=submit],button{padding:6px 16px;border:0;border-radius:6px;background:#5b3b8c;color:#fff;font-size:15px;cursor:pointer}
table{border-collapse:collapse;width:100%} th,td{border-bottom:1px solid #e1e5f0;padding:5px 10px;text-align:left;font-size:15px} th{background:#efeaf8}
.result{font-size:20px;font-weight:700;color:#1b7a3d;margin-top:10px;display:block;min-height:26px} .err,.validation-message{color:#b3261e;font-weight:700}
.pager a{margin-right:10px} .muted{color:#7a829c} .progress{color:#5b3b8c;font-weight:700;margin-left:12px} a.cmd{color:#b3261e;cursor:pointer;text-decoration:underline}"""


def layout(title, body, script=""):
    return (f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>{title}</title><style>{CSS}</style></head><body>'
            f'<div id="header"><b>旅平險服務（舊系統）</b><a href="/webforms/Quote.aspx">保費試算</a>'
            f'<a href="/webforms/Policies.aspx">保單查詢</a><a href="/blazor/policies">新版保單管理</a></div>'
            f'<div id="main">{body}</div><script>{script}</script></body></html>')


# ---------- WebForms 風格：保費試算（完整 postback） ----------
def quote_page(form):
    region = form.get("ctl00$MainContent$ddlRegion", "asia")
    plans = REGIONS[region][2]
    plan = form.get("ctl00$MainContent$ddlPlan", plans[0])
    if plan not in plans:
        plan = plans[0]
    age, days = form.get("ctl00$MainContent$txtAge", ""), form.get("ctl00$MainContent$txtDays", "")
    result = errors = ""
    if "ctl00$MainContent$btnCalc" in form:              # 按下「試算」造成的 postback
        msgs = []
        if not age.strip():
            msgs.append(f'<span id="{P}rfvAge" class="err">請輸入年齡</span>')
        if not days.strip():
            msgs.append(f'<span id="{P}rfvDays" class="err">請輸入天數</span>')
        if not msgs:
            try:
                premium = round(calc_premium(int(age), int(days)) * REGIONS[region][1] * (1.5 if "豪華" in plan else 1))
                result = f"保費 {premium} 元"
            except ValueError as e:
                msgs.append(f'<span id="{P}cvRange" class="err">{html.escape(str(e))}</span>')
        errors = " ".join(msgs)
    # 設定 USE_LABELS=1：模擬開發人員替 Label 加上 AssociatedControlID 之後產生的 <label for>
    if os.environ.get("USE_LABELS") == "1":
        lab = lambda name, text: f'<label for="{P}txt{name}" id="{P}lbl{name}">{text}</label>'
    else:
        lab = lambda name, text: f'<span id="{P}lbl{name}">{text}</span>'
    opt = lambda v, text, cur: f'<option value="{v}"{" selected" if v == cur else ""}>{text}</option>'
    body = f"""<h2>保費試算</h2>
<form method="post" action="/webforms/Quote.aspx" id="aspnetForm">
<input type="hidden" name="__EVENTTARGET" id="__EVENTTARGET" value=""><input type="hidden" name="__EVENTARGUMENT" id="__EVENTARGUMENT" value="">
<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUKLTI2NDU5ODc0Mg9kFgJmD2QWAgIDD2QWAgIBD2QWBAIBDxBkZBYBZmQCAw8QZGQWAWZk">
<div class="box">
<span id="{P}lblRegion">地區</span> <select name="ctl00$MainContent$ddlRegion" id="{P}ddlRegion" onchange="javascript:setTimeout('__doPostBack(\\'ctl00$MainContent$ddlRegion\\',\\'\\')', 0)">
{"".join(opt(k, v[0], region) for k, v in REGIONS.items())}</select>
<span id="{P}lblPlan">方案</span> <select name="ctl00$MainContent$ddlPlan" id="{P}ddlPlan">{"".join(opt(p, p, plan) for p in plans)}</select>
{lab("Age", "年齡")} <input name="ctl00$MainContent$txtAge" type="text" id="{P}txtAge" class="num" value="{html.escape(age)}">
{lab("Days", "天數")} <input name="ctl00$MainContent$txtDays" type="text" id="{P}txtDays" class="num" value="{html.escape(days)}">
<input type="submit" name="ctl00$MainContent$btnCalc" value="試算" id="{P}btnCalc">
<span id="{P}lblResult" class="result">{result}</span>{errors}</div></form>
<p class="muted">歐洲為亞洲的 1.2 倍、美洲 1.5 倍；豪華型再乘 1.5。</p>"""
    script = ("function __doPostBack(t,a){var f=document.getElementById('aspnetForm');"
              "f.__EVENTTARGET.value=t;f.__EVENTARGUMENT.value=a;f.submit();}")
    return layout("保費試算", body, script)


# ---------- WebForms 風格：保單查詢（UpdatePanel 局部更新） ----------
PAGE_SIZE = 5


def grid_html(keyword="", page_no=1):
    rows = [p for p in POLICIES if keyword in p["holder"]]
    pages = max(1, -(-len(rows) // PAGE_SIZE))
    page_no = min(page_no, pages)
    shown = rows[(page_no - 1) * PAGE_SIZE: page_no * PAGE_SIZE]
    g = P + "gvPolicies"
    trs = ""
    for i, p in enumerate(shown, 2):                     # GridView 的資料列 id 從 ctl02 開始
        cmd = (f'<a id="{g}_ctl{i:02d}_lnkCancel" class="cmd" href="javascript:void(0)" '
               f"onclick=\"if(confirm('確定要註銷 {p['no']} 嗎？'))partial('cancel','{p['no']}')\">註銷</a>") if p["status"] == "有效" else ""
        trs += (f'<tr><td>{p["no"]}</td><td>{html.escape(p["holder"])}</td><td>{p["age"]}</td><td>{p["days"]}</td>'
                f'<td>{p["premium"]}</td><td><span id="{g}_ctl{i:02d}_lblStatus">{p["status"]}</span></td><td>{cmd}</td></tr>')
    if not shown:
        trs = '<tr><td colspan="7">查無資料</td></tr>'
    pager = "".join(f'<span>{n}</span> ' if n == page_no else f'<a href="javascript:void(0)" onclick="partial(\'page\',\'{n}\')">{n}</a>'
                    for n in range(1, pages + 1))
    return (f'<table id="{g}" cellspacing="0"><tr><th scope="col">保單號碼</th><th scope="col">要保人</th><th scope="col">年齡</th>'
            f'<th scope="col">天數</th><th scope="col">保費</th><th scope="col">狀態</th><th scope="col">&nbsp;</th></tr>{trs}</table>'
            f'<div class="pager">{pager}</div><span id="{P}lblCount" class="muted">共 {len(rows)} 筆</span>')


def policies_page():
    body = f"""<h2>保單查詢</h2><form id="aspnetForm" onsubmit="return false">
<div class="box"><span id="{P}lblKeyword">要保人</span> <input type="text" id="{P}txtKeyword" name="ctl00$MainContent$txtKeyword">
<input type="submit" value="查詢" id="{P}btnSearch" onclick="partial('search','')">
<span id="{P}UpdateProgress1" class="progress" style="display:none">處理中，請稍候…</span></div>
<div class="box" id="{P}upList">{grid_html()}</div></form>"""
    script = f"""var state={{page:1}};
async function partial(action,arg){{ var pr=document.getElementById('{P}UpdateProgress1'); pr.style.display='inline';
  if(action==='page')state.page=Number(arg); if(action==='search')state.page=1;
  var r=await fetch('/webforms/Policies.aspx/partial',{{method:'POST',headers:{{'Content-Type':'application/json'}},
    body:JSON.stringify({{action:action,arg:arg,page:state.page,keyword:document.getElementById('{P}txtKeyword').value}})}});
  document.getElementById('{P}upList').innerHTML=await r.text(); pr.style.display='none'; }}"""
    return layout("保單查詢", body, script)


# ---------- Blazor 風格：新版保單管理（預先呈現 → 變成可互動 → 非同步載入資料） ----------
def blazor_page():
    body = """<div id="app"><h2>新版保單管理</h2>
<div class="box"><label for="holder">要保人</label> <input type="text" id="holder">
<label for="age">年齡</label> <input type="text" id="age" class="num"> <label for="days">天數</label> <input type="text" id="days" class="num">
<button type="button" id="add">新增保單</button><div class="validation-message" role="alert"></div></div>
<div class="box"><label for="kw">搜尋</label> <input type="text" id="kw" placeholder="輸入姓名即時篩選"><div id="list"><p><em>Loading...</em></p></div></div></div>"""
    script = """
// 模擬 Blazor：畫面先由伺服器「預先呈現」，約 0.8 秒後才與伺服器連線、變成可以互動
const $=id=>document.getElementById(id); let items=[], timer=null;
function render(){ const kw=$('kw').value.trim(); const rows=items.filter(p=>p.holder.includes(kw));
  // 每次重新呈現都換掉整個表格，就像元件重新渲染
  $('list').innerHTML = rows.length ? '<table><thead><tr><th>保單號碼</th><th>要保人</th><th>年齡</th><th>天數</th><th>保費</th><th>狀態</th></tr></thead><tbody>'+
    rows.map(p=>`<tr><td>${p.no}</td><td>${p.holder}</td><td>${p.age}</td><td>${p.days}</td><td>${p.premium}</td><td>${p.status}</td></tr>`).join('')+
    '</tbody></table><p class="muted" data-testid="count">共 '+rows.length+' 筆</p>' : '<p>沒有符合的保單</p>'; }
async function load(){ const r=await fetch('/blazor/api/policies'); items=await r.json(); render(); }
setTimeout(()=>{   // 「互動」開始：這時候事件處理常式才掛上去
  $('add').addEventListener('click',async()=>{ const al=document.querySelector('.validation-message'); al.textContent='';
    const r=await fetch('/blazor/api/policies',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({holder:$('holder').value,age:$('age').value,days:$('days').value})});
    if(r.ok){ $('holder').value='';$('age').value='';$('days').value=''; load(); } else { al.textContent=(await r.json()).error; } });
  $('kw').addEventListener('input',()=>{ clearTimeout(timer); timer=setTimeout(render,300); });   // 輸入後 0.3 秒才篩選
  document.getElementById('app').setAttribute('data-interactive','true');
  load();
}, 800);"""
    return layout("新版保單管理", body, script)


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

    def _handle(self, method):
        path = urlparse(self.path).path
        raw = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode("utf-8")
        if path == "/":
            return self._send(303, "", headers={"Location": "/webforms/Quote.aspx"})
        if path == "/webforms/Quote.aspx":
            form = {k: v[0] for k, v in parse_qs(raw, keep_blank_values=True).items()}
            if method == "POST":
                time.sleep(DELAY)                        # postback：整頁送回伺服器再重新產生
            return self._send(200, quote_page(form))
        if path == "/webforms/Policies.aspx":
            return self._send(200, policies_page())
        if path == "/webforms/Policies.aspx/partial":
            time.sleep(DELAY)                            # 局部更新也要等伺服器
            body = json.loads(raw)
            if body["action"] == "cancel":
                for p in POLICIES:
                    if p["no"] == body["arg"]:
                        p["status"] = "已註銷"
            return self._send(200, grid_html(body.get("keyword", ""), int(body.get("page", 1))))
        if path == "/blazor/policies":
            return self._send(200, blazor_page())
        if path == "/blazor/api/policies" and method == "GET":
            time.sleep(DELAY)
            return self._send(200, json.dumps(POLICIES, ensure_ascii=False), "application/json; charset=utf-8")
        if path == "/blazor/api/policies" and method == "POST":
            time.sleep(DELAY)
            body = json.loads(raw)
            try:
                if not body["holder"].strip():
                    raise ValueError("請輸入要保人")
                p = add_policy(body["holder"], int(body["age"] or 0), int(body["days"] or 0))
            except ValueError as e:
                msg = str(e) if "invalid literal" not in str(e) else "年齡與天數必須是數字"
                return self._send(422, json.dumps({"error": msg}, ensure_ascii=False), "application/json; charset=utf-8")
            return self._send(201, json.dumps(p, ensure_ascii=False), "application/json; charset=utf-8")
        if path == "/test/reset" and method == "POST":   # 只給練習用：把資料還原成初始狀態
            reset()
            return self._send(200, "ok", "text/plain")
        self._send(404, layout("找不到頁面", "<h2>找不到頁面</h2>"))

    def do_GET(self):
        self._handle("GET")

    def do_POST(self):
        self._handle("POST")

    def log_message(self, *args):
        pass


def make_server(port=0):
    reset()
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    print("練習網站啟動：http://127.0.0.1:8000")
    make_server(8000).serve_forever()
