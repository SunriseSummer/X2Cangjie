func sumUpTo(n: Int64): Int64 {
    var total: Int64 = 0
    for (i in 1..n + 1) {
        total = total + i
    }
    return total
}

main() {
    println("sum(1..10) = ${sumUpTo(10)}")
    return 0
}
