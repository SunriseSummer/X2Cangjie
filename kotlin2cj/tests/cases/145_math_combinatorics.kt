// Math utilities: modular arithmetic, combinatorics
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

fun modPow(base: Long, exp: Long, mod: Long): Long {
    var result = 1L
    var b = base % mod
    var e = exp
    while (e > 0) {
        if (e % 2 == 1L) {
            result = result * b % mod
        }
        e = e / 2
        b = b * b % mod
    }
    return result
}

fun combinations(n: Int, k: Int): Long {
    if (k > n) return 0
    if (k == 0 || k == n) return 1
    val dp = ArrayList<ArrayList<Long>>()
    for (i in 0..n) {
        val row = ArrayList<Long>()
        for (j in 0..k) {
            row.add(0)
        }
        dp.add(row)
    }
    for (i in 0..n) {
        dp[i][0] = 1
        if (i <= k) dp[i][i] = 1
    }
    for (i in 2..n) {
        for (j in 1 until i) {
            if (j <= k) {
                dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]
            }
        }
    }
    return dp[n][k]
}

fun isPerfectSquare(n: Int): Boolean {
    if (n < 0) return false
    var lo = 0
    var hi = n
    while (lo <= hi) {
        val mid = lo + (hi - lo) / 2
        val sq = mid.toLong() * mid.toLong()
        if (sq == n.toLong()) return true
        if (sq < n.toLong()) lo = mid + 1 else hi = mid - 1
    }
    return false
}

fun main() {
    // GCD tests
    println("gcd(12,8) = ${gcd(12, 8)}")
    println("gcd(100,75) = ${gcd(100, 75)}")
    println("gcd(17,13) = ${gcd(17, 13)}")

    // Modular exponentiation
    println("modPow(2,10,1000) = ${modPow(2, 10, 1000)}")
    println("modPow(3,13,1000000007) = ${modPow(3, 13, 1000000007)}")

    // Combinations
    println("C(5,2) = ${combinations(5, 2)}")
    println("C(10,3) = ${combinations(10, 3)}")
    println("C(20,10) = ${combinations(20, 10)}")

    // Perfect square check
    for (n in arrayListOf(0, 1, 4, 9, 15, 16, 25, 26, 100)) {
        println("isPerfSq($n) = ${isPerfectSquare(n)}")
    }
}
