func factorial(n: Int64): Int64 {
    if (n <= 1) {
        return 1
    }
    return n * factorial(n - 1)
}

main() {
    println(factorial(5))
    return 0
}
