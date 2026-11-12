no = "  tp-001 "
print(no.strip().upper())                 # 去空白、轉大寫
print(no.strip().replace("-", ""))
print("TP" in no.upper(), len(no))

parts = "30,5,150".split(",")             # 切開變成 list
print(parts, int(parts[0]) + 1)
print(" / ".join(["報價", "投保", "出單"]))

premium = 1234567.5
print(f"保費 {premium:,.0f} 元，折扣 {0.15:.0%}")
