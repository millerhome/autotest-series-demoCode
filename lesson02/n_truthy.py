for value in [0, "", [], None, "0", [0]]:
    print(repr(value), bool(value))

rows = []
if not rows:                 # 空的 list 當作 False
    print("查無資料")

email = None
if email is None:            # 判斷 None 請用 is
    print("沒有填 email")
