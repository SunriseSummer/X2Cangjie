func sumTo(n: Int64): Int64 {
    var total = 0
    for (i in 1..=n) {
        total += i
    }
    return total
}

main() {
    println(sumTo(10))
    return 0
}
