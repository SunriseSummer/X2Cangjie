// Quick Sort (Lomuto partition)
fun quickSort(arr: ArrayList<Int>, low: Int, high: Int) {
    if (low < high) {
        val pi = partition(arr, low, high)
        quickSort(arr, low, pi - 1)
        quickSort(arr, pi + 1, high)
    }
}

fun partition(arr: ArrayList<Int>, low: Int, high: Int): Int {
    val pivot = arr[high]
    var i = low - 1
    for (j in low until high) {
        if (arr[j] <= pivot) {
            i++
            val tmp = arr[i]
            arr[i] = arr[j]
            arr[j] = tmp
        }
    }
    val tmp = arr[i + 1]
    arr[i + 1] = arr[high]
    arr[high] = tmp
    return i + 1
}

fun printArray(arr: ArrayList<Int>) {
    val parts = ArrayList<String>()
    for (x in arr) {
        parts.add(x.toString())
    }
    println(parts.joinToString(" "))
}

fun main() {
    val a = arrayListOf(10, 7, 8, 9, 1, 5)
    quickSort(a, 0, a.size - 1)
    printArray(a)

    val b = arrayListOf(3, 6, 1, 8, 2, 9, 4, 7, 5)
    quickSort(b, 0, b.size - 1)
    printArray(b)
}
