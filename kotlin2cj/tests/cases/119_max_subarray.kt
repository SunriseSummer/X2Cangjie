// Maximum Subarray Sum (Kadane's Algorithm)
fun maxSubarraySum(arr: ArrayList<Int>): Int {
    var maxSum = arr[0]
    var currentSum = arr[0]
    for (i in 1 until arr.size) {
        if (currentSum + arr[i] > arr[i]) {
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

fun main() {
    val a = arrayListOf(-2, 1, -3, 4, -1, 2, 1, -5, 4)
    println("Max subarray sum: ${maxSubarraySum(a)}")

    val b = arrayListOf(1, 2, 3, 4, 5)
    println("Max subarray sum: ${maxSubarraySum(b)}")

    val c = arrayListOf(-1, -2, -3)
    println("Max subarray sum: ${maxSubarraySum(c)}")
}
