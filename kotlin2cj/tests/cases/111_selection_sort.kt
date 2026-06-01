// Selection Sort
fun selectionSort(arr: ArrayList<Int>) {
    val n = arr.size
    for (i in 0 until n - 1) {
        var minIdx = i
        for (j in i + 1 until n) {
            if (arr[j] < arr[minIdx]) {
                minIdx = j
            }
        }
        if (minIdx != i) {
            val tmp = arr[i]
            arr[i] = arr[minIdx]
            arr[minIdx] = tmp
        }
    }
}

fun printArray(arr: ArrayList<Int>) {
    val parts = ArrayList<String>()
    for (x in arr) {
        parts.add(x.toString())
    }
    println(parts.joinToString(" "))
}

fun main() {
    val a = arrayListOf(29, 10, 14, 37, 13)
    selectionSort(a)
    printArray(a)

    val b = arrayListOf(3, 1, 4, 1, 5, 9, 2, 6)
    selectionSort(b)
    printArray(b)
}
