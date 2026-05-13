func fib(n: Int64): Int64 {
    if (n < 2) {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

main() {
    println(fib(10))
    return 0
}
