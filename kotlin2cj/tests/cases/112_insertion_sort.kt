// Insertion Sort
fun insertionSort(arr: ArrayList<Int>) {
    for (i in 1 until arr.size) {
        val key = arr[i]
        var j = i - 1
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j]
            j--
        }
        arr[j + 1] = key
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
    val a = arrayListOf(12, 11, 13, 5, 6)
    insertionSort(a)
    printArray(a)

    val b = arrayListOf(9, 7, 5, 3, 1, 2, 4, 6, 8)
    insertionSort(b)
    printArray(b)
}
