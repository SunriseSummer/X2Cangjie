// Matrix multiplication
fun matMul(a: ArrayList<ArrayList<Int>>, b: ArrayList<ArrayList<Int>>): ArrayList<ArrayList<Int>> {
    val rows = a.size
    val cols = b[0].size
    val inner = b.size
    val result = ArrayList<ArrayList<Int>>()
    for (i in 0 until rows) {
        val row = ArrayList<Int>()
        for (j in 0 until cols) {
            var sum = 0
            for (k in 0 until inner) {
                sum += a[i][k] * b[k][j]
            }
            row.add(sum)
        }
        result.add(row)
    }
    return result
}

fun printMatrix(m: ArrayList<ArrayList<Int>>) {
    for (row in m) {
        val parts = ArrayList<String>()
        for (v in row) {
            parts.add(v.toString())
        }
        println(parts.joinToString(" "))
    }
}

fun main() {
    val a = arrayListOf(
        arrayListOf(1, 2),
        arrayListOf(3, 4)
    )
    val b = arrayListOf(
        arrayListOf(5, 6),
        arrayListOf(7, 8)
    )
    println("A * B:")
    printMatrix(matMul(a, b))

    val c = arrayListOf(
        arrayListOf(1, 0, 0),
        arrayListOf(0, 1, 0),
        arrayListOf(0, 0, 1)
    )
    val d = arrayListOf(
        arrayListOf(2, 3, 4),
        arrayListOf(5, 6, 7),
        arrayListOf(8, 9, 10)
    )
    println("I * D:")
    printMatrix(matMul(c, d))
}
