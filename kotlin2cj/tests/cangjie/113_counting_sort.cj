import std.collection.*

func countingSort(arr: ArrayList<Int64>): ArrayList<Int64> {
    if (arr.isEmpty()) {
        return arr
    }
    var maxVal = arr[0]
    for (x in arr) {
        if (x > maxVal) {
            maxVal = x
        }
    }
    let count = ArrayList<Int64>()
    for (i in 0..=maxVal) {
        count.add(0)
    }
    for (x in arr) {
        count[x] = count[x] + 1
    }
    let result = ArrayList<Int64>()
    for (i in 0..=maxVal) {
        for (j in 0..count[i]) {
            result.add(i)
        }
    }
    return result
}

func printArray(arr: ArrayList<Int64>) {
    let parts = ArrayList<String>()
    for (x in arr) {
        parts.add(x.toString())
    }
    println(String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " "))
}

main() {
    let a = ArrayList([4, 2, 2, 8, 3, 3, 1])
    printArray(countingSort(a))
    let b = ArrayList([0, 5, 3, 2, 1, 4, 3, 2])
    printArray(countingSort(b))
}
