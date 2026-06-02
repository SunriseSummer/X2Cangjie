import std.collection.*

func maxSubarraySum(arr: ArrayList<Int64>): Int64 {
    var maxSum = arr[0]
    var currentSum = arr[0]
    for (i in 1..arr.size) {
        if ((currentSum + arr[i]) > arr[i]) {
            currentSum = currentSum + arr[i]
        } else {
            currentSum = arr[i]
        }
        if (currentSum > maxSum) {
            maxSum = currentSum
        }
    }
    return maxSum
}

main() {
    let a = ArrayList([-2, 1, -3, 4, -1, 2, 1, -5, 4])
    println("Max subarray sum: ${maxSubarraySum(a)}")
    let b = ArrayList([1, 2, 3, 4, 5])
    println("Max subarray sum: ${maxSubarraySum(b)}")
    let c = ArrayList([-1, -2, -3])
    println("Max subarray sum: ${maxSubarraySum(c)}")
}
