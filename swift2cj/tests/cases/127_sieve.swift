// Small #1 (iter9): prime sieve and factor counts
func sieve(_ n: Int) -> [Int] {
    var isPrime: [Bool] = []
    var i = 0
    while i <= n {
        isPrime.append(true)
        i += 1
    }
    if n >= 0 { isPrime[0] = false }
    if n >= 1 { isPrime[1] = false }
    var p = 2
    while p * p <= n {
        if isPrime[p] {
            var k = p * p
            while k <= n {
                isPrime[k] = false
                k += p
            }
        }
        p += 1
    }
    var out: [Int] = []
    i = 0
    while i <= n {
        if isPrime[i] { out.append(i) }
        i += 1
    }
    return out
}

for n in [1, 2, 10, 30, 50] {
    print("n=\(n) primes=\(sieve(n))")
}
