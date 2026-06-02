import std.collection.*

func knapsack(weights: ArrayList<Int64>, values: ArrayList<Int64>, capacity: Int64): Int64 {
    let n = weights.size
    let dp = ArrayList<ArrayList<Int64>>()
    for (i in 0..=n) {
        let row = ArrayList<Int64>()
        for (j in 0..=capacity) {
            row.add(0)
        }
        dp.add(row)
    }
    for (i in 1..=n) {
        for (w in 1..=capacity) {
            if (weights[i - 1] <= w) {
                let take = values[i - 1] + dp[i - 1][w - weights[i - 1]]
                let skip = dp[i - 1][w]
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

main() {
    let weights = ArrayList([2, 3, 4, 5])
    let values = ArrayList([3, 4, 5, 6])
    println("Max value: ${knapsack(weights, values, 8)}")
    let w2 = ArrayList([1, 2, 3])
    let v2 = ArrayList([6, 10, 12])
    println("Max value: ${knapsack(w2, v2, 5)}")
    let w3 = ArrayList([10])
    let v3 = ArrayList([100])
    println("Max value: ${knapsack(w3, v3, 5)}")
}
