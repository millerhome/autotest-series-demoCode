def add_case(case, cases=[]):        # 危險：預設值只建立一次
    cases.append(case)
    return cases


print(add_case("A"))
print(add_case("B"))                 # 咦？A 還在


def add_case_ok(case, cases=None):   # 正確寫法
    if cases is None:
        cases = []
    cases.append(case)
    return cases


print(add_case_ok("A"), add_case_ok("B"))
