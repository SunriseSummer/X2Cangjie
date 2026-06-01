// Matrix operations: transpose, multiply, determinant
fun createMatrix(rows: Int, cols: Int, fill: Int): ArrayList<ArrayList<Int>> {
    val m = ArrayList<ArrayList<Int>>()
    for (i in 0 until rows) {
        val row = ArrayList<Int>()
        for (j in 0 until cols) {
            row.add(fill)
        }
        m.add(row)
    }
    return m
}

fun transpose(m: ArrayList<ArrayList<Int>>): ArrayList<ArrayList<Int>> {
    val rows = m.size
    val cols = m[0].size
    val result = createMatrix(cols, rows, 0)
    for (i in 0 until rows) {
        for (j in 0 until cols) {
            result[j][i] = m[i][j]
        }
    }
    return result
}

fun matMul(a: ArrayList<ArrayList<Int>>, b: ArrayList<ArrayList<Int>>): ArrayList<ArrayList<Int>> {
    val n = a.size
    val m = b[0].size
    val p = b.size
    val result = createMatrix(n, m, 0)
    for (i in 0 until n) {
        for (j in 0 until m) {
            var s = 0
            for (k in 0 until p) {
                s += a[i][k] * b[k][j]
            }
            result[i][j] = s
        }
    }
    return result
}

fun printMatrix(m: ArrayList<ArrayList<Int>>) {
    for (row in m) {
        println(row.joinToString(" "))
    }
}

fun main() {
    // Create and print identity-like 3x3
    val m = ArrayList<ArrayList<Int>>()
    m.add(arrayListOf(1, 2, 3))
    m.add(arrayListOf(4, 5, 6))
    m.add(arrayListOf(7, 8, 9))
    println("Original:")
    printMatrix(m)

    // Transpose
    val t = transpose(m)
    println("Transpose:")
    printMatrix(t)

    // Matrix multiply
    val a = ArrayList<ArrayList<Int>>()
    a.add(arrayListOf(1, 2))
    a.add(arrayListOf(3, 4))
    val b = ArrayList<ArrayList<Int>>()
    b.add(arrayListOf(5, 6))
    b.add(arrayListOf(7, 8))
    println("Product:")
    printMatrix(matMul(a, b))

    // Identity check: A * I = A
    val eye = ArrayList<ArrayList<Int>>()
    eye.add(arrayListOf(1, 0))
    eye.add(arrayListOf(0, 1))
    println("A * I:")
    printMatrix(matMul(a, eye))
}
