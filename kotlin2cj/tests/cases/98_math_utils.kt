// Math utilities: various numeric algorithms
fun gcd(a: Int, b: Int): Int {
    var x = a
    var y = b
    while (y != 0) {
        val t = y
        y = x % y
        x = t
    }
    return x
}

fun lcm(a: Int, b: Int): Int = a / gcd(a, b) * b

fun isPrime(n: Int): Boolean {
    if (n < 2) return false
    if (n == 2) return true
    if (n % 2 == 0) return false
    var i = 3
    while (i * i <= n) {
        if (n % i == 0) return false
        i += 2
    }
    return true
}

fun primeFactors(n: Int): ArrayList<Int> {
    val factors = ArrayList<Int>()
    var num = n
    var d = 2
    while (d * d <= num) {
        while (num % d == 0) {
            factors.add(d)
            num /= d
        }
        d++
    }
    if (num > 1) factors.add(num)
    return factors
}

fun pow(base: Int, exp: Int): Long {
    var result = 1L
    for (i in 0 until exp) {
        result *= base
    }
    return result
}

fun digitSum(n: Int): Int {
    var sum = 0
    var num = n
    while (num > 0) {
        sum += num % 10
        num /= 10
    }
    return sum
}

fun main() {
    println("gcd(12,8) = ${gcd(12, 8)}")
    println("gcd(100,75) = ${gcd(100, 75)}")
    println("lcm(4,6) = ${lcm(4, 6)}")
    println("lcm(12,18) = ${lcm(12, 18)}")

    val primes = ArrayList<Int>()
    for (i in 2..30) {
        if (isPrime(i)) primes.add(i)
    }
    println("Primes up to 30: ${primes.joinToString(" ")}")

    println("Factors of 60: ${primeFactors(60).joinToString(" * ")}")
    println("Factors of 97: ${primeFactors(97).joinToString(" * ")}")
    println("Factors of 360: ${primeFactors(360).joinToString(" * ")}")

    println("2^10 = ${pow(2, 10)}")
    println("3^5 = ${pow(3, 5)}")

    println("digitSum(12345) = ${digitSum(12345)}")
    println("digitSum(9999) = ${digitSum(9999)}")

    // Check: sum of first N primes
    var s = 0
    for (p in primes) s += p
    println("Sum of primes to 30: $s")
}
