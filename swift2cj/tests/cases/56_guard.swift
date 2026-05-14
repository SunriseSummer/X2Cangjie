// guard with early return
func sign(_ x: Int) -> Int {
    guard x != 0 else { return 0 }
    return x > 0 ? 1 : -1
}
func divide(_ a: Int, _ b: Int) -> Int {
    guard b != 0 else { return -1 }
    return a / b
}
print(sign(-7))
print(sign(0))
print(sign(42))
print(divide(10, 2))
print(divide(10, 0))
