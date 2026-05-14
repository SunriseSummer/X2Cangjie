var xs: [Int] = [1, 2, 3, 4, 5]
var ys: [Int] = []
var i: Int = xs.count - 1
while i >= 0 {
    ys.append(xs[i])
    i = i - 1
}
for v in ys {
    print(v)
}
