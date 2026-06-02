import std.collection.*

func coinChange(coins: ArrayList<Int64>, amount: Int64): Int64 {
    let inf = amount + 1
    let dp = ArrayList<Int64>()
    for (i in 0..=amount) {
        dp.add(inf)
    }
    dp[0] = 0
    for (i in 1..=amount) {
        for (c in coins) {
            if ((c <= i) && ((dp[i - c] + 1) < dp[i])) {
                dp[i] = dp[i - c] + 1
            }
        }
    }
    if (dp[amount] > amount) {
        return -1
    }
    return dp[amount]
}

main() {
    let coins1 = ArrayList([1, 5, 10, 25])
    println("Coins for 30: ${coinChange(coins1, 30)}")
    println("Coins for 11: ${coinChange(coins1, 11)}")
    let coins2 = ArrayList([2])
    println("Coins for 3: ${coinChange(coins2, 3)}")
    let coins3 = ArrayList([1, 3, 4])
    println("Coins for 6: ${coinChange(coins3, 6)}")
}
