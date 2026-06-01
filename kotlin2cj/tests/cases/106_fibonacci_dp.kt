// Fibonacci with memoization (bottom-up DP)
fun fibonacci(n: Int): Long {
    if (n <= 1) return n.toLong()
    val dp = ArrayList<Long>()
    dp.add(0L)
    dp.add(1L)
    for (i in 2..n) {
        dp.add(dp[i - 1] + dp[i - 2])
    }
    return dp[n]
}

fun main() {
    for (i in 0..10) {
        println("fib($i) = ${fibonacci(i)}")
    }
    println("fib(30) = ${fibonacci(30)}")
    println("fib(40) = ${fibonacci(40)}")
}
