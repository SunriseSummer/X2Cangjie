// Binary Search
fun binarySearch(arr: ArrayList<Int>, target: Int): Int {
    var lo = 0
    var hi = arr.size - 1
    while (lo <= hi) {
        val mid = lo + (hi - lo) / 2
        if (arr[mid] == target) {
            return mid
        } else if (arr[mid] < target) {
            lo = mid + 1
        } else {
            hi = mid - 1
        }
    }
    return -1
}

fun main() {
    val arr = arrayListOf(1, 3, 5, 7, 9, 11, 13, 15)
    println("Find 7: index ${binarySearch(arr, 7)}")
    println("Find 1: index ${binarySearch(arr, 1)}")
    println("Find 15: index ${binarySearch(arr, 15)}")
    println("Find 6: index ${binarySearch(arr, 6)}")
}
