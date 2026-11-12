policy = {"no": "TP001", "age": 30, "days": 5}   # 類似 Dictionary

print(policy["no"])
print(policy.get("email"))            # 沒有這個 key：回傳 None
print(policy.get("email", "未填"))    # 也可以給預設值

policy["premium"] = 150               # 新增或修改
for key, value in policy.items():
    print(key, "=", value)

print("age" in policy, "email" in policy)
