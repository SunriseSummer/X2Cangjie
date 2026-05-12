// ternary expressions
func absv(_ x: Int) -> Int {
    return x >= 0 ? x : -x
}
func maxv(_ a: Int, _ b: Int) -> Int {
    return a > b ? a : b
}
func minv(_ a: Int, _ b: Int) -> Int {
    return a < b ? a : b
}
print(absv(-9))
print(absv(7))
print(maxv(3, 5))
print(minv(3, 5))
let parity = (100 % 2 == 0) ? "even" : "odd"
print(parity)
