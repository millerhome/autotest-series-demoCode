from decimal import Decimal, ROUND_HALF_UP

print(7 / 2, 7 // 2, 7 % 2)        # 小數除法、整數除法、餘數
print(round(52.5), round(53.5))    # 四捨六入五成雙
print(0.1 + 0.2)                   # 浮點數誤差

amount = Decimal("52.5")           # 金額請用 Decimal
print(amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
