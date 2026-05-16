main() {
    var n = 5
    var dp = Array<Int64>(n, {_ => 0})
    for (i in 0..n) {
        dp[i] = i * i
    }
    for (i in 0..n) {
        println(dp[i])
    }
    return 0
}
