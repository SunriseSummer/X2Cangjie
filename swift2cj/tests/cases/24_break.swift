var s: Int = 0
for i in 0..<20 {
    if i == 5 {
        break
    }
    s = s + i
}
print(s)
var t: Int = 0
for i in 0..<10 {
    if i % 2 == 0 {
        continue
    }
    t = t + i
}
print(t)
