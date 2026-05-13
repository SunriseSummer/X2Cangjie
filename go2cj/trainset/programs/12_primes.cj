func isPrime(n: Int64): Bool {
    if (n < 2) {
        return false
    }
    var i = 2
    while (i * i <= n) {
        if (n % i == 0) {
            return false
        }
        i++
    }
    return true
}

main() {
    var count = 0
    var n = 2
    while (count < 5) {
        if (isPrime(n)) {
            println(n)
            count++
        }
        n++
    }
    return 0
}
