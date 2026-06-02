import std.collection.*

func lis(arr: ArrayList<Int64>): Int64 {
    let n = arr.size
    if (n == 0) {
        return 0
    }
    let dp = ArrayList<Int64>()
    for (i in 0..n) {
        dp.add(1)
    }
    for (i in 1..n) {
        for (j in 0..i) {
            if ((arr[j] < arr[i]) && ((dp[j] + 1) > dp[i])) {
                dp[i] = dp[j] + 1
            }
        }
    }
    var maxLen = 0
    for (v in dp) {
        if (v > maxLen) {
            maxLen = v
        }
    }
    return maxLen
}

main() {
    let a = ArrayList([10, 9, 2, 5, 3, 7, 101, 18])
    println("LIS length: ${lis(a)}")
    let b = ArrayList([0, 1, 0, 3, 2, 3])
    println("LIS length: ${lis(b)}")
    let c = ArrayList([7, 7, 7, 7])
    println("LIS length: ${lis(c)}")
}
