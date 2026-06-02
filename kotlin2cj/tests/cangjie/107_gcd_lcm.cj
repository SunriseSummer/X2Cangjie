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
    return (a / gcd(a, b)) * b
}

main() {
    println("gcd(12, 8) = ${gcd(12, 8)}")
    println("gcd(54, 24) = ${gcd(54, 24)}")
    println("gcd(7, 13) = ${gcd(7, 13)}")
    println("lcm(4, 6) = ${lcm(4, 6)}")
    println("lcm(12, 15) = ${lcm(12, 15)}")
    println("lcm(7, 5) = ${lcm(7, 5)}")
}
