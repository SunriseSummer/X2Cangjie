class Matrix(val rows: Int, val cols: Int) {
    val data = ArrayList<ArrayList<Int>>()

    init {
        for (i in 0 until rows) {
            val row = ArrayList<Int>()
            for (j in 0 until cols) {
                row.add(0)
            }
            data.add(row)
        }
    }

    fun set(r: Int, c: Int, value: Int) {
        data[r][c] = value
    }

    fun get(r: Int, c: Int): Int = data[r][c]

    fun add(other: Matrix): Matrix {
        val result = Matrix(rows, cols)
        for (i in 0 until rows) {
            for (j in 0 until cols) {
                result.set(i, j, get(i, j) + other.get(i, j))
            }
        }
        return result
    }

    fun multiply(other: Matrix): Matrix {
        val result = Matrix(rows, other.cols)
        for (i in 0 until rows) {
            for (j in 0 until other.cols) {
                var sum = 0
                for (k in 0 until cols) {
                    sum += get(i, k) * other.get(k, j)
                }
                result.set(i, j, sum)
            }
        }
        return result
    }

    fun transpose(): Matrix {
        val result = Matrix(cols, rows)
        for (i in 0 until rows) {
            for (j in 0 until cols) {
                result.set(j, i, get(i, j))
            }
        }
        return result
    }

    fun print() {
        for (i in 0 until rows) {
            val sb = StringBuilder()
            for (j in 0 until cols) {
                if (j > 0) sb.append(" ")
                sb.append(get(i, j))
            }
            println(sb.toString())
        }
    }
}
