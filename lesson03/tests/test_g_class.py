from premium import calc_premium


class TestChildPremium:
    def test_newborn(self):
        assert calc_premium(0, 5) == 120

    def test_seventeen(self):
        assert calc_premium(17, 5) == 120
