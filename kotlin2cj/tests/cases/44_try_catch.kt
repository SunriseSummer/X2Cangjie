fun safeDiv(a: Int, b: Int): Int {
    try {
        if (b == 0) {
            throw Exception("div by zero")
        }
        return a / b
    } catch (e: Exception) {
        println("error caught")
        return -1
    } finally {
        println("done")
    }
}
fun main() {
    println(safeDiv(10, 2))
    println(safeDiv(10, 0))
}
