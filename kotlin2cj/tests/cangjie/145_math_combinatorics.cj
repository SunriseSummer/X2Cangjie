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

func modPow(base: Int64, exp: Int64, mod: Int64): Int64 {
    var result = 1
    var b = base % mod
    var e = exp
    while (e > 0) {
        if ((e % 2) == 1) {
            result = (result * b) % mod
        }
        e = e / 2
        b = (b * b) % mod
    }
    return result
}

func combinations(n: Int64, k: Int64): Int64 {
    if (k > n) {
        return 0
    }
    if ((k == 0) || (k == n)) {
        return 1
    }
    let dp = ArrayList<ArrayList<Int64>>()
    for (i in 0..=n) {
        let row = ArrayList<Int64>()
        for (j in 0..=k) {
            row.add(0)
        }
        dp.add(row)
    }
    for (i in 0..=n) {
        dp[i][0] = 1
        if (i <= k) {
            dp[i][i] = 1
        }
    }
    for (i in 2..=n) {
        for (j in 1..i) {
            if (j <= k) {
                dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]
            }
        }
    }
    return dp[n][k]
}

func isPerfectSquare(n: Int64): Bool {
    if (n < 0) {
        return false
    }
    var lo = 0
    var hi = n
    while (lo <= hi) {
        let mid = lo + ((hi - lo) / 2)
        let sq = Int64(mid) * Int64(mid)
        if (sq == Int64(n)) {
            return true
        }
        if (sq < Int64(n)) {
            lo = mid + 1
        } else {
            hi = mid - 1
        }
    }
    return false
}

main() {
    println("gcd(12,8) = ${gcd(12, 8)}")
    println("gcd(100,75) = ${gcd(100, 75)}")
    println("gcd(17,13) = ${gcd(17, 13)}")
    println("modPow(2,10,1000) = ${modPow(2, 10, 1000)}")
    println("modPow(3,13,1000000007) = ${modPow(3, 13, 1000000007)}")
    println("C(5,2) = ${combinations(5, 2)}")
    println("C(10,3) = ${combinations(10, 3)}")
    println("C(20,10) = ${combinations(20, 10)}")
    for (n in ArrayList([0, 1, 4, 9, 15, 16, 25, 26, 100])) {
        println("isPerfSq(${n}) = ${isPerfectSquare(n)}")
    }
}
