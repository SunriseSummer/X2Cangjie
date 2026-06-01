// Counting Sort
fun countingSort(arr: ArrayList<Int>): ArrayList<Int> {
    if (arr.isEmpty()) return arr
    var maxVal = arr[0]
    for (x in arr) {
        if (x > maxVal) maxVal = x
    }
    val count = ArrayList<Int>()
    for (i in 0..maxVal) {
        count.add(0)
    }
    for (x in arr) {
        count[x] = count[x] + 1
    }
    val result = ArrayList<Int>()
    for (i in 0..maxVal) {
        for (j in 0 until count[i]) {
            result.add(i)
        }
    }
    return result
}

fun printArray(arr: ArrayList<Int>) {
    val parts = ArrayList<String>()
    for (x in arr) {
        parts.add(x.toString())
    }
    println(parts.joinToString(" "))
}

fun main() {
    val a = arrayListOf(4, 2, 2, 8, 3, 3, 1)
    printArray(countingSort(a))

    val b = arrayListOf(0, 5, 3, 2, 1, 4, 3, 2)
    printArray(countingSort(b))
}
