func fact(n: Int64): Int64 {
    if (n <= 1) {
        return 1
    }
    return n * fact(n - 1)
}

main() {
    println("5! = ${fact(5)}")
    return 0
}
