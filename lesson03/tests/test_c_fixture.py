def test_new_store_is_empty(store):
    assert store.count() == 0


def test_add_policy(store):
    store.add("TP100", "林小美", 120)
    assert store.count() == 1
    assert store.get("TP100")["holder"] == "林小美"


def test_find_existing(store_with_data):
    assert store_with_data.count() == 2
    assert store_with_data.get("TP002")["premium"] == 225


def test_use_rates(rates):
    assert rates["base_per_day"] == 30
