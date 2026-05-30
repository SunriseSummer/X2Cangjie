fun main() {
    val a = mutableListOf(5, 2, 8, 1, 9, 3, 7)
    val n = a.size
    for (i in 0 until n) {
        for (j in 0 until n - 1 - i) {
            if (a[j] > a[j + 1]) {
                val tmp = a[j]
                a[j] = a[j + 1]
                a[j + 1] = tmp
            }
        }
    }
    for (x in a) {
        print("$x ")
    }
    println("")
}
