import pytest


@pytest.fixture(scope="session")
def connection():
    print("\n  [session] 建立連線")
    yield "conn"
    print("\n  [session] 關閉連線")


@pytest.fixture
def test_data(connection):
    print("\n  [function] 建立測試資料")
    yield {"no": "TP001"}
    print("\n  [function] 清除測試資料")


def test_one(test_data):
    print("  執行 test_one")


def test_two(test_data):
    print("  執行 test_two")
    assert test_data["no"] == "TP999"      # 故意失敗：清理還是會執行
