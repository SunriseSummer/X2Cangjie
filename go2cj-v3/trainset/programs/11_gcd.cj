func gcd(a0: Int64, b0: Int64): Int64 {
    var a = a0
    var b = b0
    while (b != 0) {
        var t = a % b
        a = b
        b = t
    }
    return a
}

main() {
    println(gcd(48, 18))
    println(gcd(100, 75))
    println(gcd(7, 13))
    return 0
}
