a = [1, 2]
b = a
b.append(3)
print(a)
print([1, 2] == [1, 2], [1, 2] is [1, 2])
c = a.copy()
c.append(4)
print(a, c)
