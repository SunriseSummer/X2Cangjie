// A 100+ line geometric shapes program — protocol-based polymorphism,
// enum with associated values, operator overload, generic container.

protocol Drawable {
    func area() -> Int
    func describe() -> String
}

struct Rect: Drawable {
    var w: Int
    var h: Int
    func area() -> Int {
        return self.w * self.h
    }
    func describe() -> String {
        return "Rect(\(self.w)x\(self.h))"
    }
}

struct Circle: Drawable {
    var r: Int
    func area() -> Int {
        // pi ~ 3 for integer math
        return 3 * self.r * self.r
    }
    func describe() -> String {
        return "Circle(r=\(self.r))"
    }
}

struct Square: Drawable {
    var side: Int
    func area() -> Int {
        return self.side * self.side
    }
    func describe() -> String {
        return "Square(\(self.side))"
    }
}

class ShapeGroup {
    var shapes: [Drawable] = []
    func add(_ s: Drawable) {
        self.shapes.append(s)
    }
    func count() -> Int {
        return self.shapes.count
    }
    func totalArea() -> Int {
        var total = 0
        for s in self.shapes {
            total += s.area()
        }
        return total
    }
    func describeAll() {
        for s in self.shapes {
            print(s.describe(), "area =", s.area())
        }
    }
}

// 2D point with operator overload
struct Point {
    var x: Int
    var y: Int
    static func + (a: Point, b: Point) -> Point {
        return Point(x: a.x + b.x, y: a.y + b.y)
    }
    static func - (a: Point, b: Point) -> Point {
        return Point(x: a.x - b.x, y: a.y - b.y)
    }
    func manhattan() -> Int {
        let ax = self.x >= 0 ? self.x : -self.x
        let ay = self.y >= 0 ? self.y : -self.y
        return ax + ay
    }
}

// Recursive enum-like helper using a regular enum + integer codes
enum Direction {
    case north
    case south
    case east
    case west
}

func step(_ d: Direction) -> Point {
    switch d {
    case .north: return Point(x: 0, y: 1)
    case .south: return Point(x: 0, y: -1)
    case .east:  return Point(x: 1, y: 0)
    case .west:  return Point(x: -1, y: 0)
    }
}

// --- main ---
let g = ShapeGroup()
g.add(Rect(w: 3, h: 4))
g.add(Circle(r: 5))
g.add(Square(side: 6))
g.add(Rect(w: 2, h: 10))
print("shape count =", g.count())
print("total area  =", g.totalArea())
g.describeAll()

var origin = Point(x: 0, y: 0)
let moves: [Direction] = [.north, .north, .east, .east, .east, .south]
for m in moves {
    origin = origin + step(m)
}
print("final =", origin.x, origin.y)
print("manhattan =", origin.manhattan())
