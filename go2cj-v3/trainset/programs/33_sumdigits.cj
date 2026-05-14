func sumDigits(n: Int64): Int64 {
    var m = n
    var total = 0
    while (m > 0) {
        total += m % 10
        m /= 10
    }
    return total
}

main() {
    println(sumDigits(12345))
    println(sumDigits(987))
    return 0
}
