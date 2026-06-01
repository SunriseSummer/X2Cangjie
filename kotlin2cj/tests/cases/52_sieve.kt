fun main() {
    val n = 50
    val sieve = mutableListOf<Boolean>()
    for (k in 0..n) {
        sieve.add(true)
    }
    sieve[0] = false
    sieve[1] = false
    var i = 2
    while (i * i <= n) {
        if (sieve[i]) {
            var j = i * i
            while (j <= n) {
                sieve[j] = false
                j += i
            }
        }
        i += 1
    }
    var count = 0
    for (k in 2..n) {
        if (sieve[k]) {
            count += 1
        }
    }
    println("primes up to $n: $count")
}
