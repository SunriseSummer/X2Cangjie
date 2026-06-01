// Coin Change Problem (DP)
fun coinChange(coins: ArrayList<Int>, amount: Int): Int {
    val inf = amount + 1
    val dp = ArrayList<Int>()
    for (i in 0..amount) {
        dp.add(inf)
    }
    dp[0] = 0
    for (i in 1..amount) {
        for (c in coins) {
            if (c <= i && dp[i - c] + 1 < dp[i]) {
                dp[i] = dp[i - c] + 1
            }
        }
    }
    if (dp[amount] > amount) {
        return -1
    }
    return dp[amount]
}

fun main() {
    val coins1 = arrayListOf(1, 5, 10, 25)
    println("Coins for 30: ${coinChange(coins1, 30)}")
    println("Coins for 11: ${coinChange(coins1, 11)}")

    val coins2 = arrayListOf(2)
    println("Coins for 3: ${coinChange(coins2, 3)}")

    val coins3 = arrayListOf(1, 3, 4)
    println("Coins for 6: ${coinChange(coins3, 6)}")
}
