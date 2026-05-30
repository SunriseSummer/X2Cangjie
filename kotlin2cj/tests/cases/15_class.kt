class Point(val x: Int, val y: Int) {
    fun sumSquares(): Int {
        return x * x + y * y
    }
}
fun main() {
    val p = Point(3, 4)
    println("x=${p.x} y=${p.y} r2=${p.sumSquares()}")
}
