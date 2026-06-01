// Complex loop patterns: nested loops with break, accumulation patterns
fun findPrimes(limit: Int): ArrayList<Int> {
    val primes = ArrayList<Int>()
    for (n in 2..limit) {
        var isPrime = true
        for (d in 2 until n) {
            if (d * d > n) break
            if (n % d == 0) {
                isPrime = false
                break
            }
        }
        if (isPrime) primes.add(n)
    }
    return primes
}

fun spiralOrder(n: Int): ArrayList<Int> {
    val matrix = ArrayList<ArrayList<Int>>()
    for (i in 0 until n) {
        val row = ArrayList<Int>()
        for (j in 0 until n) {
            row.add(i * n + j + 1)
        }
        matrix.add(row)
    }

    val result = ArrayList<Int>()
    var top = 0
    var bottom = n - 1
    var left = 0
    var right = n - 1

    while (top <= bottom && left <= right) {
        for (j in left..right) result.add(matrix[top][j])
        top++
        for (i in top..bottom) result.add(matrix[i][right])
        right--
        if (top <= bottom) {
            for (j in right downTo left) result.add(matrix[bottom][j])
            bottom--
        }
        if (left <= right) {
            for (i in bottom downTo top) result.add(matrix[i][left])
            left++
        }
    }
    return result
}

fun pascalTriangle(rows: Int): ArrayList<ArrayList<Int>> {
    val tri = ArrayList<ArrayList<Int>>()
    for (i in 0 until rows) {
        val row = ArrayList<Int>()
        for (j in 0..i) {
            if (j == 0 || j == i) {
                row.add(1)
            } else {
                row.add(tri[i - 1][j - 1] + tri[i - 1][j])
            }
        }
        tri.add(row)
    }
    return tri
}

fun main() {
    // Primes up to 30
    val primes = findPrimes(30)
    println("Primes: ${primes.joinToString(" ")}")

    // Spiral order of 3x3 matrix
    val spiral = spiralOrder(3)
    println("Spiral: ${spiral.joinToString(" ")}")

    // Spiral 4x4
    val spiral4 = spiralOrder(4)
    println("Spiral4: ${spiral4.joinToString(" ")}")

    // Pascal's triangle
    val pascal = pascalTriangle(5)
    for (row in pascal) {
        println(row.joinToString(" "))
    }
}
