ages = [17, 30, 65]            # list：類似 List<int>
ages.append(80)
print(ages[0], ages[-1], len(ages))
print(ages[1:3])               # 切片：索引 1 到 2

seniors = [a for a in ages if a >= 65]     # 類似 LINQ 的 Where
doubled = [a * 2 for a in ages]            # 類似 Select
print(seniors, doubled)

point = (25.03, 121.56)        # tuple：建立後不能修改
lat, lng = point               # 解構
print(lat, lng)
