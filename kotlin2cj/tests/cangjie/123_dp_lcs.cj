import std.collection.*

func lcs(s1: String, s2: String): Int64 {
    let m = s1.size
    let n = s2.size
    let dp = ArrayList<ArrayList<Int64>>()
    for (i in 0..=m) {
        let row = ArrayList<Int64>()
        for (j in 0..=n) {
            row.add(0)
        }
        dp.add(row)
    }
    for (i in 1..=m) {
        for (j in 1..=n) {
            if (s1.toRuneArray()[i - 1] == s2.toRuneArray()[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1] + 1
            } else {
                if (dp[i - 1][j] > dp[i][j - 1]) {
                    dp[i][j] = dp[i - 1][j]
                } else {
                    dp[i][j] = dp[i][j - 1]
                }
            }
        }
    }
    return dp[m][n]
}

main() {
    println("LCS(ABCBDAB, BDCAB) = ${lcs("ABCBDAB", "BDCAB")}")
    println("LCS(abc, abc) = ${lcs("abc", "abc")}")
    println("LCS(abc, def) = ${lcs("abc", "def")}")
    println("LCS(AGGTAB, GXTXAYB) = ${lcs("AGGTAB", "GXTXAYB")}")
}
