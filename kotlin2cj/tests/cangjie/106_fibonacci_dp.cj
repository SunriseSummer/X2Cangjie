import std.collection.*

func fibonacci(n: Int64): Int64 {
    if (n <= 1) {
        return Int64(n)
    }
    let dp = ArrayList<Int64>()
    dp.add(0)
    dp.add(1)
    for (i in 2..=n) {
        dp.add(dp[i - 1] + dp[i - 2])
    }
    return dp[n]
}

main() {
    for (i in 0..=10) {
        println("fib(${i}) = ${fibonacci(i)}")
    }
    println("fib(30) = ${fibonacci(30)}")
    println("fib(40) = ${fibonacci(40)}")
}
