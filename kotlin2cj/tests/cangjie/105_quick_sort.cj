import std.collection.*

func quickSort(arr: ArrayList<Int64>, low: Int64, high: Int64): Unit {
    if (low < high) {
        let pi = partition(arr, low, high)
        quickSort(arr, low, pi - 1)
        quickSort(arr, pi + 1, high)
    }
}

func partition(arr: ArrayList<Int64>, low: Int64, high: Int64): Int64 {
    let pivot = arr[high]
    var i = low - 1
    for (j in low..high) {
        if (arr[j] <= pivot) {
            i += 1
            let tmp = arr[i]
            arr[i] = arr[j]
            arr[j] = tmp
        }
    }
    let tmp = arr[i + 1]
    arr[i + 1] = arr[high]
    arr[high] = tmp
    return i + 1
}

func printArray(arr: ArrayList<Int64>) {
    let parts = ArrayList<String>()
    for (x in arr) {
        parts.add(x.toString())
    }
    println(String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " "))
}

main() {
    let a = ArrayList([10, 7, 8, 9, 1, 5])
    quickSort(a, 0, a.size - 1)
    printArray(a)
    let b = ArrayList([3, 6, 1, 8, 2, 9, 4, 7, 5])
    quickSort(b, 0, b.size - 1)
    printArray(b)
}
