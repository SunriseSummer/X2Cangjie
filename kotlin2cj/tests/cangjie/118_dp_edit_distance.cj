import std.collection.*

func editDistance(s1: String, s2: String): Int64 {
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
    for (i in 0..=m) {
        dp[i][0] = i
    }
    for (j in 0..=n) {
        dp[0][j] = j
    }
    for (i in 1..=m) {
        for (j in 1..=n) {
            if (s1.toRuneArray()[i - 1] == s2.toRuneArray()[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1]
            } else {
                let insert = dp[i][j - 1] + 1
                let delete = dp[i - 1][j] + 1
                let replace = dp[i - 1][j - 1] + 1
                var minVal = insert
                if (delete < minVal) {
                    minVal = delete
                }
                if (replace < minVal) {
                    minVal = replace
                }
                dp[i][j] = minVal
            }
        }
    }
    return dp[m][n]
}

main() {
    println("kitten -> sitting: ${editDistance("kitten", "sitting")}")
    println("abc -> abc: ${editDistance("abc", "abc")}")
    println("empty -> hello: ${editDistance("", "hello")}")
    println("horse -> ros: ${editDistance("horse", "ros")}")
}
