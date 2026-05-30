fun main() {
    val m = mutableListOf(
        mutableListOf(1, 2, 3),
        mutableListOf(4, 5, 6)
    )
    var sum = 0
    for (row in m) {
        for (v in row) {
            sum += v
        }
    }
    println("sum=$sum")
    println("m[1][2]=${m[1][2]}")
}
