func lcs(a: String, b: String): Int64 {
    let m = a.size
    let n = b.size
    var dp = Array<Array<Int64>>(m + 1, {_ => Array<Int64>(n + 1, {_ => 0})})
    for (i in 1..=m) {
        for (j in 1..=n) {
            if (a[i - 1] == b[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1] + 1
            } else if (dp[i - 1][j] > dp[i][j - 1]) {
                dp[i][j] = dp[i - 1][j]
            } else {
                dp[i][j] = dp[i][j - 1]
            }
        }
    }
    return dp[m][n]
}

main() {
    println(lcs("ABCBDAB", "BDCAB"))
    return 0
}
