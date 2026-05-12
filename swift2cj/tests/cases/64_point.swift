// 2D point with operator overload, distance method, and formatted print
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
    func describe() -> String {
        return "(\(self.x), \(self.y))"
    }
}
let p1 = Point(x: 3, y: 4)
let p2 = Point(x: -1, y: 2)
let sum = p1 + p2
let diff = p1 - p2
print(sum.describe())
print(diff.describe())
print(p1.manhattan())
print(p2.manhattan())
