"""把「網址、逾時、共用標頭」集中在一個地方的小幫手。"""
import requests


class ApiClient:
    def __init__(self, base_url, timeout=5):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["Accept"] = "application/json"

    def request(self, method, path, **kwargs):
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, self.base_url + path, **kwargs)

    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self.request("POST", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)

    def login(self, username, password):
        r = self.post("/api/login", json={"username": username, "password": password})
        assert r.status_code == 200, f"登入失敗：{r.status_code} {r.text}"
        self.session.headers["Authorization"] = f"Bearer {r.json()['token']}"

    def close(self):
        self.session.close()
