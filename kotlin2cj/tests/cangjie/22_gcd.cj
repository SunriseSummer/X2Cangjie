func gcd(a: Int64, b: Int64): Int64 {
    var x = a
    var y = b
    while (y != 0) {
        let t = y
        y = x % y
        x = t
    }
    return x
}

main() {
    println("gcd(48,36)=${gcd(48, 36)}")
    println("gcd(17,5)=${gcd(17, 5)}")
}
