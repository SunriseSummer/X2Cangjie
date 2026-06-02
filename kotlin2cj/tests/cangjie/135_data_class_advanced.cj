import std.collection.*

class Point <: ToString {
    let x: Int64
    let y: Int64
    init(x: Int64, y: Int64) {
        this.x = x
        this.y = y
    }
    public func toString(): String {
        return "Point(x=${this.x}, y=${this.y})"
    }
}

class Line <: ToString {
    let start: Point
    let end: Point
    init(start: Point, end: Point) {
        this.start = start
        this.end = end
    }
    public func toString(): String {
        return "Line(start=${this.start}, end=${this.end})"
    }
}

func manhattanDistance(a: Point, b: Point): Int64 {
    let dx = a.x - b.x
    let dy = a.y - b.y
    let absDx = if (dx < 0) {
        -dx
    } else {
        dx
    }
    let absDy = if (dy < 0) {
        -dy
    } else {
        dy
    }
    return absDx + absDy
}

func closestPair(points: ArrayList<Point>): Int64 {
    var minDist = 999999
    for (i in 0..points.size) {
        for (j in (i + 1)..points.size) {
            let d = manhattanDistance(points[i], points[j])
            if (d < minDist) {
                minDist = d
            }
        }
    }
    return minDist
}

main() {
    let p1 = Point(1, 2)
    let p2 = Point(4, 6)
    println(p1)
    println(p2)
    println("Distance: ${manhattanDistance(p1, p2)}")
    let line = Line(p1, p2)
    println("Line: ${line}")
    let points = ArrayList([Point(0, 0), Point(3, 4), Point(1, 1), Point(5, 2)])
    println("Closest pair distance: ${closestPair(points)}")
    let sorted = ArrayList<Point>()
    for (p in points) {
        sorted.add(p)
    }
    for (i in 0..sorted.size) {
        for (j in (i + 1)..sorted.size) {
            if ((sorted[i].x > sorted[j].x) || ((sorted[i].x == sorted[j].x) && (sorted[i].y > sorted[j].y))) {
                let tmp = sorted[i]
                sorted[i] = sorted[j]
                sorted[j] = tmp
            }
        }
    }
    for (p in sorted) {
        println("  ${p}")
    }
}
