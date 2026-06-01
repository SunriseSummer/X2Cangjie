import std.collection.*

main() {
    let matrix = ArrayList([ArrayList([1, 2, 3]), ArrayList([4, 5, 6]), ArrayList([7, 8, 9])])
    var trace = 0
    for (i in 0..3) {
        trace += matrix[i][i]
    }
    println("trace=${trace}")
    for (row in matrix) {
        println(String.join(collectArray<String>(row.iterator().map({e => e.toString()})), delimiter: " "))
    }
    let flat = collectArrayList(matrix.iterator().map({ it => it.iterator().fold<Int64>(0, {acc, x => acc + x}) }))
    println("rowSums=${String.join(collectArray<String>(flat.iterator().map({e => e.toString()})), delimiter: ",")}")
}
