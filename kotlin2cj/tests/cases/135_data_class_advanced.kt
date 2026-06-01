// Advanced data class usage: nested data classes, collections of data classes
data class Point(val x: Int, val y: Int)
data class Line(val start: Point, val end: Point)

fun manhattanDistance(a: Point, b: Point): Int {
    val dx = a.x - b.x
    val dy = a.y - b.y
    val absDx = if (dx < 0) -dx else dx
    val absDy = if (dy < 0) -dy else dy
    return absDx + absDy
}

fun closestPair(points: ArrayList<Point>): Int {
    var minDist = 999999
    for (i in 0 until points.size) {
        for (j in i + 1 until points.size) {
            val d = manhattanDistance(points[i], points[j])
            if (d < minDist) {
                minDist = d
            }
        }
    }
    return minDist
}

fun main() {
    val p1 = Point(1, 2)
    val p2 = Point(4, 6)
    println(p1)
    println(p2)
    println("Distance: ${manhattanDistance(p1, p2)}")

    val line = Line(p1, p2)
    println("Line: $line")

    // Collection of points
    val points = arrayListOf(
        Point(0, 0),
        Point(3, 4),
        Point(1, 1),
        Point(5, 2)
    )
    println("Closest pair distance: ${closestPair(points)}")

    // Sorting points by x then y
    val sorted = ArrayList<Point>()
    for (p in points) sorted.add(p)
    for (i in 0 until sorted.size) {
        for (j in i + 1 until sorted.size) {
            if (sorted[i].x > sorted[j].x || (sorted[i].x == sorted[j].x && sorted[i].y > sorted[j].y)) {
                val tmp = sorted[i]
                sorted[i] = sorted[j]
                sorted[j] = tmp
            }
        }
    }
    for (p in sorted) {
        println("  $p")
    }
}
