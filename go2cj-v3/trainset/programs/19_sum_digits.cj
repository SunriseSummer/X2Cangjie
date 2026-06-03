func sumDigits(n: Int64): Int64 {
    var total = 0
    var m = n
    while (m > 0) {
        total += m % 10
        m /= 10
    }
    return total
}

main() {
    println(sumDigits(12345))
    println(sumDigits(987654))
    println(sumDigits(0))
    println(sumDigits(7))
    return 0
}
