// Bubble Sort
fun bubbleSort(arr: ArrayList<Int>) {
    val n = arr.size
    for (i in 0 until n - 1) {
        for (j in 0 until n - 1 - i) {
            if (arr[j] > arr[j + 1]) {
                val tmp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = tmp
            }
        }
    }
}

fun printArray(arr: ArrayList<Int>) {
    val parts = ArrayList<String>()
    for (x in arr) {
        parts.add(x.toString())
    }
    println(parts.joinToString(", "))
}

fun main() {
    val a = arrayListOf(64, 34, 25, 12, 22, 11, 90)
    bubbleSort(a)
    printArray(a)

    val b = arrayListOf(5, 1, 4, 2, 8)
    bubbleSort(b)
    printArray(b)

    val c = arrayListOf(1)
    bubbleSort(c)
    printArray(c)
}
