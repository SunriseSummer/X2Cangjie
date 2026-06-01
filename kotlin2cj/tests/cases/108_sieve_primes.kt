// Sieve of Eratosthenes
fun sieve(limit: Int): ArrayList<Int> {
    val isPrime = ArrayList<Boolean>()
    for (i in 0..limit) {
        isPrime.add(true)
    }
    isPrime[0] = false
    if (limit >= 1) isPrime[1] = false
    var p = 2
    while (p * p <= limit) {
        if (isPrime[p]) {
            var m = p * p
            while (m <= limit) {
                isPrime[m] = false
                m += p
            }
        }
        p++
    }
    val primes = ArrayList<Int>()
    for (i in 2..limit) {
        if (isPrime[i]) primes.add(i)
    }
    return primes
}

fun main() {
    val primes = sieve(50)
    val parts = ArrayList<String>()
    for (p in primes) {
        parts.add(p.toString())
    }
    println("Primes up to 50: ${parts.joinToString(", ")}")
    println("Count: ${primes.size}")
}
