import std.collection.*

func matMul(a: ArrayList<ArrayList<Int64>>, b: ArrayList<ArrayList<Int64>>): ArrayList<ArrayList<Int64>> {
    let rows = a.size
    let cols = b[0].size
    let inner = b.size
    let result = ArrayList<ArrayList<Int64>>()
    for (i in 0..rows) {
        let row = ArrayList<Int64>()
        for (j in 0..cols) {
            var sum = 0
            for (k in 0..inner) {
                sum += a[i][k] * b[k][j]
            }
            row.add(sum)
        }
        result.add(row)
    }
    return result
}

func printMatrix(m: ArrayList<ArrayList<Int64>>) {
    for (row in m) {
        let parts = ArrayList<String>()
        for (v in row) {
            parts.add(v.toString())
        }
        println(String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " "))
    }
}

main() {
    let a = ArrayList([ArrayList([1, 2]), ArrayList([3, 4])])
    let b = ArrayList([ArrayList([5, 6]), ArrayList([7, 8])])
    println("A * B:")
    printMatrix(matMul(a, b))
    let c = ArrayList([ArrayList([1, 0, 0]), ArrayList([0, 1, 0]), ArrayList([0, 0, 1])])
    let d = ArrayList([ArrayList([2, 3, 4]), ArrayList([5, 6, 7]), ArrayList([8, 9, 10])])
    println("I * D:")
    printMatrix(matMul(c, d))
}
