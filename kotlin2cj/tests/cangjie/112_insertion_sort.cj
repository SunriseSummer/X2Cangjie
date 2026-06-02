import std.collection.*

func insertionSort(arr: ArrayList<Int64>) {
    for (i in 1..arr.size) {
        let key = arr[i]
        var j = i - 1
        while ((j >= 0) && (arr[j] > key)) {
            arr[j + 1] = arr[j]
            j -= 1
        }
        arr[j + 1] = key
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
    let a = ArrayList([12, 11, 13, 5, 6])
    insertionSort(a)
    printArray(a)
    let b = ArrayList([9, 7, 5, 3, 1, 2, 4, 6, 8])
    insertionSort(b)
    printArray(b)
}
