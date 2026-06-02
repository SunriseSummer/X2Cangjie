import std.collection.*

func createMatrix(rows: Int64, cols: Int64, fill: Int64): ArrayList<ArrayList<Int64>> {
    let m = ArrayList<ArrayList<Int64>>()
    for (i in 0..rows) {
        let row = ArrayList<Int64>()
        for (j in 0..cols) {
            row.add(fill)
        }
        m.add(row)
    }
    return m
}

func transpose(m: ArrayList<ArrayList<Int64>>): ArrayList<ArrayList<Int64>> {
    let rows = m.size
    let cols = m[0].size
    let result = createMatrix(cols, rows, 0)
    for (i in 0..rows) {
        for (j in 0..cols) {
            result[j][i] = m[i][j]
        }
    }
    return result
}

func matMul(a: ArrayList<ArrayList<Int64>>, b: ArrayList<ArrayList<Int64>>): ArrayList<ArrayList<Int64>> {
    let n = a.size
    let m = b[0].size
    let p = b.size
    let result = createMatrix(n, m, 0)
    for (i in 0..n) {
        for (j in 0..m) {
            var s = 0
            for (k in 0..p) {
                s += a[i][k] * b[k][j]
            }
            result[i][j] = s
        }
    }
    return result
}

func printMatrix(m: ArrayList<ArrayList<Int64>>) {
    for (row in m) {
        println(String.join(collectArray<String>(row.iterator().map({e => e.toString()})), delimiter: " "))
    }
}

main() {
    let m = ArrayList<ArrayList<Int64>>()
    m.add(ArrayList([1, 2, 3]))
    m.add(ArrayList([4, 5, 6]))
    m.add(ArrayList([7, 8, 9]))
    println("Original:")
    printMatrix(m)
    let t = transpose(m)
    println("Transpose:")
    printMatrix(t)
    let a = ArrayList<ArrayList<Int64>>()
    a.add(ArrayList([1, 2]))
    a.add(ArrayList([3, 4]))
    let b = ArrayList<ArrayList<Int64>>()
    b.add(ArrayList([5, 6]))
    b.add(ArrayList([7, 8]))
    println("Product:")
    printMatrix(matMul(a, b))
    let eye = ArrayList<ArrayList<Int64>>()
    eye.add(ArrayList([1, 0]))
    eye.add(ArrayList([0, 1]))
    println("A * I:")
    printMatrix(matMul(a, eye))
}
