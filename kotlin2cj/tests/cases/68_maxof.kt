fun main() {
    val a = 3
    val b = 7
    println(maxOf(a, b))
    println(minOf(a, b))
    println(maxOf(10, minOf(4, 9)))
    var best = 0
    for (x in listOf(5, 2, 8, 1)) {
        best = maxOf(best, x)
    }
    println(best)
}
