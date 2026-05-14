class Shape {
    func area() -> Int {
        return 0
    }
}
class Rect: Shape {
    var w: Int
    var h: Int
    init(_ w: Int, _ h: Int) {
        self.w = w
        self.h = h
    }
    override func area() -> Int {
        return self.w * self.h
    }
}
class Sq: Shape {
    var s: Int
    init(_ s: Int) {
        self.s = s
    }
    override func area() -> Int {
        return self.s * self.s
    }
}
let shapes: [Shape] = [Rect(3, 4), Sq(5), Rect(2, 6)]
for s in shapes {
    print(s.area())
}
