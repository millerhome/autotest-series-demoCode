def parse_age(text):
    try:
        age = int(text)
    except ValueError:
        print(f"'{text}' 不是數字")
        return None
    finally:
        print("（不管成功失敗都會執行）")
    if age < 0:
        raise ValueError("年齡不可為負數")
    return age


print(parse_age("30"))
print(parse_age("三十"))
parse_age("-1")
