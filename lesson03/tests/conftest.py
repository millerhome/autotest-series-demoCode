import pytest
from policy_store import PolicyStore
from premium import load_rates


@pytest.fixture(scope="session")
def rates():
    """整個測試過程只讀一次規則檔。"""
    return load_rates()


@pytest.fixture
def store(tmp_path):
    """每個測試一個全新、空的保單庫。"""
    return PolicyStore(tmp_path / "policies.json")


@pytest.fixture
def store_with_data(store):
    """已經放好兩張保單的保單庫。"""
    store.add("TP001", "王小明", 150)
    store.add("TP002", "陳小華", 225)
    return store
