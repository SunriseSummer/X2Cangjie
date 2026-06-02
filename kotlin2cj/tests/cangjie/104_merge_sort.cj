import std.collection.*

func merge(left: ArrayList<Int64>, right: ArrayList<Int64>): ArrayList<Int64> {
    let result = ArrayList<Int64>()
    var i = 0
    var j = 0
    while ((i < left.size) && (j < right.size)) {
        if (left[i] <= right[j]) {
            result.add(left[i])
            i += 1
        } else {
            result.add(right[j])
            j += 1
        }
    }
    while (i < left.size) {
        result.add(left[i])
        i += 1
    }
    while (j < right.size) {
        result.add(right[j])
        j += 1
    }
    return result
}

func mergeSort(arr: ArrayList<Int64>): ArrayList<Int64> {
    if (arr.size <= 1) {
        return arr
    }
    let mid = arr.size / 2
    let left = ArrayList<Int64>()
    for (i in 0..mid) {
        left.add(arr[i])
    }
    let right = ArrayList<Int64>()
    for (i in mid..arr.size) {
        right.add(arr[i])
    }
    return merge(mergeSort(left), mergeSort(right))
}

func printArray(arr: ArrayList<Int64>) {
    let parts = ArrayList<String>()
    for (x in arr) {
        parts.add(x.toString())
    }
    println(String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " "))
}

main() {
    let a = ArrayList([38, 27, 43, 3, 9, 82, 10])
    printArray(mergeSort(a))
    let b = ArrayList([5, 2, 8, 1, 9])
    printArray(mergeSort(b))
}
