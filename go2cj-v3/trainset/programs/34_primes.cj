func isPrime(n: Int64): Bool {
    if (n < 2) {
        return false
    }
    var i = 2
    while (i * i <= n) {
        if (n % i == 0) {
            return false
        }
        i += 1
    }
    return true
}

main() {
    for (n in 2..12) {
        if (isPrime(n)) {
            println(n)
        }
    }
    return 0
}
