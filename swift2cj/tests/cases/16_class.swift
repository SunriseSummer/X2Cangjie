class Point {
    var x: Int
    var y: Int
    init(_ x: Int, _ y: Int) {
        self.x = x
        self.y = y
    }
    func sumSquares() -> Int {
        return self.x * self.x + self.y * self.y
    }
}
let p = Point(3, 4)
print("r2=\(p.sumSquares())")
