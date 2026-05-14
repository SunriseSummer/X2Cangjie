func isPrime(_ n: Int) -> Bool {
    if n < 2 {
        return false
    }
    var i: Int = 2
    while i * i <= n {
        if n % i == 0 {
            return false
        }
        i = i + 1
    }
    return true
}
for n in 2...10 {
    if isPrime(n) {
        print(n)
    }
}
