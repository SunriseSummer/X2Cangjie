// Merge Sort
fun merge(left: ArrayList<Int>, right: ArrayList<Int>): ArrayList<Int> {
    val result = ArrayList<Int>()
    var i = 0
    var j = 0
    while (i < left.size && j < right.size) {
        if (left[i] <= right[j]) {
            result.add(left[i])
            i++
        } else {
            result.add(right[j])
            j++
        }
    }
    while (i < left.size) {
        result.add(left[i])
        i++
    }
    while (j < right.size) {
        result.add(right[j])
        j++
    }
    return result
}

fun mergeSort(arr: ArrayList<Int>): ArrayList<Int> {
    if (arr.size <= 1) return arr
    val mid = arr.size / 2
    val left = ArrayList<Int>()
    for (i in 0 until mid) {
        left.add(arr[i])
    }
    val right = ArrayList<Int>()
    for (i in mid until arr.size) {
        right.add(arr[i])
    }
    return merge(mergeSort(left), mergeSort(right))
}

fun printArray(arr: ArrayList<Int>) {
    val parts = ArrayList<String>()
    for (x in arr) {
        parts.add(x.toString())
    }
    println(parts.joinToString(" "))
}

fun main() {
    val a = arrayListOf(38, 27, 43, 3, 9, 82, 10)
    printArray(mergeSort(a))

    val b = arrayListOf(5, 2, 8, 1, 9)
    printArray(mergeSort(b))
}
