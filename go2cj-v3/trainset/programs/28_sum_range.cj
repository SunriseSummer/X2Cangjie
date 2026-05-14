func sumRange(lo: Int64, hi: Int64): Int64 {
    var total = 0
    for (i in lo..=hi) {
        total += i
    }
    return total
}

func sumEven(lo: Int64, hi: Int64): Int64 {
    var total = 0
    for (i in lo..=hi) {
        if (i % 2 == 0) {
            total += i
        }
    }
    return total
}

main() {
    println(sumRange(1, 100))
    println(sumEven(1, 10))
    println(sumRange(0, 0))
    println(sumEven(2, 20))
    return 0
}
