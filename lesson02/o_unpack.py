names = ["小明", "小華", "小美"]
ages = [17, 30, 65]

for i, name in enumerate(names, start=1):
    print(i, name)

for name, age in zip(names, ages):
    print(f"{name} {age} 歲")

status, body = 200, {"ok": True}      # 一次指定兩個變數
print(status, body["ok"])
