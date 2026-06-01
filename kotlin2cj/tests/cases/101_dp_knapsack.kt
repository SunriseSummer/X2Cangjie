// 0/1 Knapsack Problem using Dynamic Programming
fun knapsack(weights: ArrayList<Int>, values: ArrayList<Int>, capacity: Int): Int {
    val n = weights.size
    val dp = ArrayList<ArrayList<Int>>()
    for (i in 0..n) {
        val row = ArrayList<Int>()
        for (j in 0..capacity) {
            row.add(0)
        }
        dp.add(row)
    }
    for (i in 1..n) {
        for (w in 1..capacity) {
            if (weights[i - 1] <= w) {
                val take = values[i - 1] + dp[i - 1][w - weights[i - 1]]
                val skip = dp[i - 1][w]
                if (take > skip) {
                    dp[i][w] = take
                } else {
                    dp[i][w] = skip
                }
            } else {
                dp[i][w] = dp[i - 1][w]
            }
        }
    }
    return dp[n][capacity]
}

fun main() {
    val weights = arrayListOf(2, 3, 4, 5)
    val values = arrayListOf(3, 4, 5, 6)
    println("Max value: ${knapsack(weights, values, 8)}")

    val w2 = arrayListOf(1, 2, 3)
    val v2 = arrayListOf(6, 10, 12)
    println("Max value: ${knapsack(w2, v2, 5)}")

    val w3 = arrayListOf(10)
    val v3 = arrayListOf(100)
    println("Max value: ${knapsack(w3, v3, 5)}")
}
