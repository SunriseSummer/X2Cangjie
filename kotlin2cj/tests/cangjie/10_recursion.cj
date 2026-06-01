func fact(n: Int64): Int64 {
    if (n <= 1) {
        return 1
    }
    return n * fact(n - 1)
}

func fib(n: Int64): Int64 {
    if (n < 2) {
        return n
    }
    return fib(n - 1) + fib(n - 2)
}

main() {
    println("5!=${fact(5)}")
    println("fib(10)=${fib(10)}")
}
