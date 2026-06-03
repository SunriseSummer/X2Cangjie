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

func lcm(a: Int64, b: Int64): Int64 {
    return a / gcd(a, b) * b
}

main() {
    println(lcm(4, 6))
    println(lcm(12, 18))
    println(lcm(7, 5))
    println(lcm(100, 80))
    return 0
}
