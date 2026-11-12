name = "小臻"          # 不用宣告型別，也沒有分號
age = 30
rate = 1.5
is_member = True       # True / False 第一個字母大寫
nothing = None         # 相當於 C# 的 null

print(type(name), type(age), type(rate))
print(f"{name} 今年 {age} 歲，保費 {30 * 5 * rate:.0f} 元")
