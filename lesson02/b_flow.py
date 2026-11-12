def age_group(age):
    if age < 18:
        return "未成年"
    elif age < 65:
        return "成年"
    else:
        return "年長"


for age in [17, 30, 65]:
    print(age, age_group(age))

for i in range(3):          # 0, 1, 2
    print("第", i + 1, "次")
