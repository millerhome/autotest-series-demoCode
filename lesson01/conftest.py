import threading

import pytest
from quote_service import make_server


@pytest.fixture(scope="session")
def base_url():
    server = make_server()          # port=0：由系統挑一個空的埠
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
