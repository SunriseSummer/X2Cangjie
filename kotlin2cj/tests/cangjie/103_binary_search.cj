import std.collection.*

func binarySearch(arr: ArrayList<Int64>, target: Int64): Int64 {
    var lo = 0
    var hi = arr.size - 1
    while (lo <= hi) {
        let mid = lo + ((hi - lo) / 2)
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

main() {
    let arr = ArrayList([1, 3, 5, 7, 9, 11, 13, 15])
    println("Find 7: index ${binarySearch(arr, 7)}")
    println("Find 1: index ${binarySearch(arr, 1)}")
    println("Find 15: index ${binarySearch(arr, 15)}")
    println("Find 6: index ${binarySearch(arr, 6)}")
}
