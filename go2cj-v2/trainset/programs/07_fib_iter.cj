func fib(n: Int64): Int64 {
    if (n < 2) {
        return n
    }
    var a = 0
    var b = 1
    for (_ in 2..=n) {
        var t = a + b
        a = b
        b = t
    }
    return b
}

main() {
    for (i in 0..10) {
        println(fib(i))
    }
    return 0
}
