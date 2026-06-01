data class Point(val x: Int, val y: Int)

fun dist2(a: Point, b: Point): Int {
    val dx = a.x - b.x
    val dy = a.y - b.y
    return dx * dx + dy * dy
}
fun main() {
    val p = Point(0, 0)
    val q = Point(3, 4)
    println("p=(${p.x}, ${p.y})")
    println(dist2(p, q))
}
