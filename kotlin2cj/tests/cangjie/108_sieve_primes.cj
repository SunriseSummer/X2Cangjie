import std.collection.*

func sieve(limit: Int64): ArrayList<Int64> {
    let isPrime = ArrayList<Bool>()
    for (i in 0..=limit) {
        isPrime.add(true)
    }
    isPrime[0] = false
    if (limit >= 1) {
        isPrime[1] = false
    }
    var p = 2
    while ((p * p) <= limit) {
        if (isPrime[p]) {
            var m = p * p
            while (m <= limit) {
                isPrime[m] = false
                m += p
            }
        }
        p += 1
    }
    let primes = ArrayList<Int64>()
    for (i in 2..=limit) {
        if (isPrime[i]) {
            primes.add(i)
        }
    }
    return primes
}

main() {
    let primes = sieve(50)
    let parts = ArrayList<String>()
    for (p in primes) {
        parts.add(p.toString())
    }
    println("Primes up to 50: ${String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("Count: ${primes.size}")
}
