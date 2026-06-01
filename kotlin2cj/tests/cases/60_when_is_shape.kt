open class Shape
class Circle(val r: Int) : Shape()
class Rect(val w: Int, val h: Int) : Shape()

fun area(s: Shape): Int = when (s) {
    is Circle -> 3 * s.r * s.r
    is Rect -> s.w * s.h
    else -> 0
}

fun main() {
    val shapes = listOf(Circle(2), Rect(3, 4), Circle(5))
    var total = 0
    for (sh in shapes) {
        total = total + area(sh)
    }
    println(total)
}
