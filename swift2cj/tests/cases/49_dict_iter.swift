let m: [String: Int] = ["a": 1, "b": 2, "c": 3]
var s: Int = 0
for k in ["a", "b", "c"] {
    s = s + m[k]!
}
print(s)
