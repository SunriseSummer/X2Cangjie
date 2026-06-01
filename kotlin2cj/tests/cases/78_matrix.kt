fun main() {
    val matrix = listOf(
        listOf(1, 2, 3),
        listOf(4, 5, 6),
        listOf(7, 8, 9)
    )
    var trace = 0
    for (i in 0 until 3) trace += matrix[i][i]
    println("trace=$trace")
    for (row in matrix) {
        println(row.joinToString(" "))
    }
    val flat = matrix.map { it.sum() }
    println("rowSums=${flat.joinToString(",")}")
}
