import std.collection.*

func bubbleSort(arr: ArrayList<Int64>) {
    let n = arr.size
    for (i in 0..(n - 1)) {
        for (j in 0..((n - 1) - i)) {
            if (arr[j] > arr[j + 1]) {
                let tmp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = tmp
            }
        }
    }
}

func printArray(arr: ArrayList<Int64>) {
    let parts = ArrayList<String>()
    for (x in arr) {
        parts.add(x.toString())
    }
    println(String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: ", "))
}

main() {
    let a = ArrayList([64, 34, 25, 12, 22, 11, 90])
    bubbleSort(a)
    printArray(a)
    let b = ArrayList([5, 1, 4, 2, 8])
    bubbleSort(b)
    printArray(b)
    let c = ArrayList([1])
    bubbleSort(c)
    printArray(c)
}
