def calc_premium(age: int, days: int = 1, base: int = 30) -> int:
    """計算旅平險保費。"""
    factor = 1.5 if age >= 65 else 1.0
    return round(base * days * factor)


print(calc_premium(30))                 # 只給必要參數
print(calc_premium(30, 5))              # 依位置
print(calc_premium(age=65, days=5))     # 依名稱
print(calc_premium(30, base=50))        # 跳過中間的參數
print(calc_premium("30", 5))            # 型別提示不會擋你
