func fact(n: Int64): Int64 {
    if (n <= 1) {
        return 1
    }
    return n * fact(n - 1)
}

main() {
    for (i in 1..=6) {
        println(fact(i))
    }
    return 0
}
