import std.collection.*

func max(a: Int64, b: Int64): Int64 {
    if (a > b) {
        return a
    }
    return b
}

func knapsack(weights: ArrayList<Int64>, values: ArrayList<Int64>, capacity: Int64): Int64 {
    var n = weights.size
    var dp = Array<Int64>(capacity + 1, {_ => 0})
    for (i in 0..n) {
        var w = capacity
        while (w >= weights[i]) {
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
            w -= 1
        }
    }
    return dp[capacity]
}

main() {
    var weights = ArrayList<Int64>([2, 3, 4, 5])
    var values = ArrayList<Int64>([3, 4, 5, 6])
    println(knapsack(weights, values, 8))
    return 0
}
