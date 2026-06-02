import std.collection.*

func findPrimes(limit: Int64): ArrayList<Int64> {
    let primes = ArrayList<Int64>()
    for (n in 2..=limit) {
        var isPrime = true
        for (d in 2..n) {
            if ((d * d) > n) {
                break
            }
            if ((n % d) == 0) {
                isPrime = false
                break
            }
        }
        if (isPrime) {
            primes.add(n)
        }
    }
    return primes
}

func spiralOrder(n: Int64): ArrayList<Int64> {
    let matrix = ArrayList<ArrayList<Int64>>()
    for (i in 0..n) {
        let row = ArrayList<Int64>()
        for (j in 0..n) {
            row.add(((i * n) + j) + 1)
        }
        matrix.add(row)
    }
    let result = ArrayList<Int64>()
    var top = 0
    var bottom = n - 1
    var left = 0
    var right = n - 1
    while ((top <= bottom) && (left <= right)) {
        for (j in left..=right) {
            result.add(matrix[top][j])
        }
        top += 1
        for (i in top..=bottom) {
            result.add(matrix[i][right])
        }
        right -= 1
        if (top <= bottom) {
            for (j in right..=left : -1) {
                result.add(matrix[bottom][j])
            }
            bottom -= 1
        }
        if (left <= right) {
            for (i in bottom..=top : -1) {
                result.add(matrix[i][left])
            }
            left += 1
        }
    }
    return result
}

func pascalTriangle(rows: Int64): ArrayList<ArrayList<Int64>> {
    let tri = ArrayList<ArrayList<Int64>>()
    for (i in 0..rows) {
        let row = ArrayList<Int64>()
        for (j in 0..=i) {
            if ((j == 0) || (j == i)) {
                row.add(1)
            } else {
                row.add(tri[i - 1][j - 1] + tri[i - 1][j])
            }
        }
        tri.add(row)
    }
    return tri
}

main() {
    let primes = findPrimes(30)
    println("Primes: ${String.join(collectArray<String>(primes.iterator().map({e => e.toString()})), delimiter: " ")}")
    let spiral = spiralOrder(3)
    println("Spiral: ${String.join(collectArray<String>(spiral.iterator().map({e => e.toString()})), delimiter: " ")}")
    let spiral4 = spiralOrder(4)
    println("Spiral4: ${String.join(collectArray<String>(spiral4.iterator().map({e => e.toString()})), delimiter: " ")}")
    let pascal = pascalTriangle(5)
    for (row in pascal) {
        println(String.join(collectArray<String>(row.iterator().map({e => e.toString()})), delimiter: " "))
    }
}
