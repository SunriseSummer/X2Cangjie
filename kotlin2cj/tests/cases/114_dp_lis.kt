// Longest Increasing Subsequence (DP)
fun lis(arr: ArrayList<Int>): Int {
    val n = arr.size
    if (n == 0) return 0
    val dp = ArrayList<Int>()
    for (i in 0 until n) {
        dp.add(1)
    }
    for (i in 1 until n) {
        for (j in 0 until i) {
            if (arr[j] < arr[i] && dp[j] + 1 > dp[i]) {
                dp[i] = dp[j] + 1
            }
        }
    }
    var maxLen = 0
    for (v in dp) {
        if (v > maxLen) maxLen = v
    }
    return maxLen
}

fun main() {
    val a = arrayListOf(10, 9, 2, 5, 3, 7, 101, 18)
    println("LIS length: ${lis(a)}")

    val b = arrayListOf(0, 1, 0, 3, 2, 3)
    println("LIS length: ${lis(b)}")

    val c = arrayListOf(7, 7, 7, 7)
    println("LIS length: ${lis(c)}")
}
