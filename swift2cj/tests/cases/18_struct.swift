struct Vec2 {
    var x: Int
    var y: Int
    func dot(_ o: Vec2) -> Int {
        return self.x * o.x + self.y * o.y
    }
}
let a = Vec2(x: 1, y: 2)
let b = Vec2(x: 3, y: 4)
print("dot=\(a.dot(b))")
