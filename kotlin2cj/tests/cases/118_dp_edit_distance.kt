// Edit Distance (Levenshtein Distance) using DP
fun editDistance(s1: String, s2: String): Int {
    val m = s1.length
    val n = s2.length
    val dp = ArrayList<ArrayList<Int>>()
    for (i in 0..m) {
        val row = ArrayList<Int>()
        for (j in 0..n) {
            row.add(0)
        }
        dp.add(row)
    }
    for (i in 0..m) dp[i][0] = i
    for (j in 0..n) dp[0][j] = j
    for (i in 1..m) {
        for (j in 1..n) {
            if (s1[i - 1] == s2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1]
            } else {
                val insert = dp[i][j - 1] + 1
                val delete = dp[i - 1][j] + 1
                val replace = dp[i - 1][j - 1] + 1
                var minVal = insert
                if (delete < minVal) minVal = delete
                if (replace < minVal) minVal = replace
                dp[i][j] = minVal
            }
        }
    }
    return dp[m][n]
}

fun main() {
    println("kitten -> sitting: ${editDistance("kitten", "sitting")}")
    println("abc -> abc: ${editDistance("abc", "abc")}")
    println("empty -> hello: ${editDistance("", "hello")}")
    println("horse -> ros: ${editDistance("horse", "ros")}")
}
