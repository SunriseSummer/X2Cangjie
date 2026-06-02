import std.collection.*

func selectionSort(arr: ArrayList<Int64>) {
    let n = arr.size
    for (i in 0..(n - 1)) {
        var minIdx = i
        for (j in (i + 1)..n) {
            if (arr[j] < arr[minIdx]) {
                minIdx = j
            }
        }
        if (minIdx != i) {
            let tmp = arr[i]
            arr[i] = arr[minIdx]
            arr[minIdx] = tmp
        }
    }
}

func printArray(arr: ArrayList<Int64>) {
    let parts = ArrayList<String>()
    for (x in arr) {
        parts.add(x.toString())
    }
    println(String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " "))
}

main() {
    let a = ArrayList([29, 10, 14, 37, 13])
    selectionSort(a)
    printArray(a)
    let b = ArrayList([3, 1, 4, 1, 5, 9, 2, 6])
    selectionSort(b)
    printArray(b)
}
