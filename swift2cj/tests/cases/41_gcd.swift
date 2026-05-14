func gcd(_ a: Int, _ b: Int) -> Int {
    var x: Int = a
    var y: Int = b
    while y != 0 {
        let t: Int = y
        y = x % y
        x = t
    }
    return x
}
print(gcd(48, 18))
print(gcd(100, 75))
print(gcd(17, 5))
