def find_policy(no):
    policies = {"TP001": {"holder": "王小明"}}
    return policies.get(no)          # 找不到時回傳 None


p = find_policy("TP999")
print(p)
print(p["holder"])
