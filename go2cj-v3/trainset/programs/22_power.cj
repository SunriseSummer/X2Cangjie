func power(base: Int64, exp: Int64): Int64 {
    if (exp == 0) {
        return 1
    }
    if (exp % 2 == 0) {
        let half = power(base, exp / 2)
        return half * half
    }
    return base * power(base, exp - 1)
}

main() {
    println(power(2, 10))
    println(power(3, 4))
    println(power(5, 0))
    println(power(7, 1))
    return 0
}
