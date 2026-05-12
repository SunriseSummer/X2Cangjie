var xs: [Int] = [1, 2, 3, 4, 5]
xs.append(6)
var s: Int = 0
for v in xs {
    s = s + v
}
print(s)
print(xs.count)
