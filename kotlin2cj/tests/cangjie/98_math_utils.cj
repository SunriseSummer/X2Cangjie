import std.collection.*

func gcd(a: Int64, b: Int64): Int64 {
    var x = a
    var y = b
    while (y != 0) {
        let t = y
        y = x % y
        x = t
    }
    return x
}

func lcm(a: Int64, b: Int64): Int64 {
    return (a / gcd(a, b)) * b
}

func isPrime(n: Int64): Bool {
    if (n < 2) {
        return false
    }
    if (n == 2) {
        return true
    }
    if ((n % 2) == 0) {
        return false
    }
    var i = 3
    while ((i * i) <= n) {
        if ((n % i) == 0) {
            return false
        }
        i += 2
    }
    return true
}

func primeFactors(n: Int64): ArrayList<Int64> {
    let factors = ArrayList<Int64>()
    var num = n
    var d = 2
    while ((d * d) <= num) {
        while ((num % d) == 0) {
            factors.add(d)
            num /= d
        }
        d += 1
    }
    if (num > 1) {
        factors.add(num)
    }
    return factors
}

func pow(base: Int64, exp: Int64): Int64 {
    var result = 1
    for (i in 0..exp) {
        result *= base
    }
    return result
}

func digitSum(n: Int64): Int64 {
    var sum = 0
    var num = n
    while (num > 0) {
        sum += num % 10
        num /= 10
    }
    return sum
}

main() {
    println("gcd(12,8) = ${gcd(12, 8)}")
    println("gcd(100,75) = ${gcd(100, 75)}")
    println("lcm(4,6) = ${lcm(4, 6)}")
    println("lcm(12,18) = ${lcm(12, 18)}")
    let primes = ArrayList<Int64>()
    for (i in 2..=30) {
        if (isPrime(i)) {
            primes.add(i)
        }
    }
    println("Primes up to 30: ${String.join(collectArray<String>(primes.iterator().map({e => e.toString()})), delimiter: " ")}")
    println("Factors of 60: ${String.join(collectArray<String>(primeFactors(60).iterator().map({e => e.toString()})), delimiter: " * ")}")
    println("Factors of 97: ${String.join(collectArray<String>(primeFactors(97).iterator().map({e => e.toString()})), delimiter: " * ")}")
    println("Factors of 360: ${String.join(collectArray<String>(primeFactors(360).iterator().map({e => e.toString()})), delimiter: " * ")}")
    println("2^10 = ${pow(2, 10)}")
    println("3^5 = ${pow(3, 5)}")
    println("digitSum(12345) = ${digitSum(12345)}")
    println("digitSum(9999) = ${digitSum(9999)}")
    var s = 0
    for (p in primes) {
        s += p
    }
    println("Sum of primes to 30: ${s}")
}
