"""旅平險保費試算（教學示意，費率為虛構）"""

BASE_PER_DAY = 30  # 每日基本保費（元）


def age_factor(age: int) -> float:
    if age < 0 or age > 80:
        raise ValueError("年齡不在承保範圍")
    if age < 18:
        return 0.8
    if age < 65:
        return 1.0
    return 1.5


def calc_premium(age: int, days: int) -> int:
    if days < 1:
        raise ValueError("天數至少 1 天")
    return round(BASE_PER_DAY * days * age_factor(age))
