// Small #2 (iter4): 2D point and rectangle with class composition
class Point {
    var x: Int
    var y: Int
    init(x: Int, y: Int) {
        self.x = x
        self.y = y
    }
    func translate(dx: Int, dy: Int) {
        x += dx
        y += dy
    }
    func distSq(_ other: Point) -> Int {
        let ax = x - other.x
        let ay = y - other.y
        return ax * ax + ay * ay
    }
}

class Rect {
    var topLeft: Point
    var width: Int
    var height: Int
    init(topLeft: Point, width: Int, height: Int) {
        self.topLeft = topLeft
        self.width = width
        self.height = height
    }
    func area() -> Int {
        return width * height
    }
    func contains(_ p: Point) -> Bool {
        if p.x < topLeft.x { return false }
        if p.x > topLeft.x + width { return false }
        if p.y < topLeft.y { return false }
        if p.y > topLeft.y + height { return false }
        return true
    }
}

let r = Rect(topLeft: Point(x: 0, y: 0), width: 10, height: 5)
print("area = \(r.area())")
print("contains (3, 3) = \(r.contains(Point(x: 3, y: 3)))")
print("contains (11, 3) = \(r.contains(Point(x: 11, y: 3)))")

let p = Point(x: 1, y: 1)
p.translate(dx: 5, dy: 3)
print("p moved to (\(p.x), \(p.y))")
print("dist^2 to (10, 10) = \(p.distSq(Point(x: 10, y: 10)))")

let r2 = Rect(topLeft: Point(x: -2, y: -2), width: 4, height: 4)
print("r2 area = \(r2.area())")
print("r2 contains (0, 0) = \(r2.contains(Point(x: 0, y: 0)))")
print("r2 contains (3, 3) = \(r2.contains(Point(x: 3, y: 3)))")
