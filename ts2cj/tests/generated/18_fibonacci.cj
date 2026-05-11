func fib(n: Int64): Int64 {
    if (n < 2) {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

main() {
    for (i in 0..8) {
        println("fib(${i}) = ${fib(i)}")
    }
    return 0
}
