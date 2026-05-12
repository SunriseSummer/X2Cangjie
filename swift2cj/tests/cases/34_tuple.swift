func divmod(_ a: Int, _ b: Int) -> (Int, Int) {
    return (a / b, a % b)
}
let r = divmod(17, 5)
print(r.0)
print(r.1)
