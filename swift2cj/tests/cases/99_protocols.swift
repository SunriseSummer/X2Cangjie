// Medium #1 (iter5): protocol + multiple conformances (Drawable + Shapes) (~130 lines)
protocol Drawable {
    func draw() -> String
    func area() -> Int
}

protocol Named {
    func label() -> String
}

class Circle: Drawable, Named {
    let radius: Int
    init(radius: Int) {
        self.radius = radius
    }
    func draw() -> String {
        return "circle(r=\(radius))"
    }
    func area() -> Int {
        return 3 * radius * radius   // pi approximated as 3
    }
    func label() -> String {
        return "C\(radius)"
    }
}

class Square: Drawable, Named {
    let side: Int
    init(side: Int) {
        self.side = side
    }
    func draw() -> String {
        return "square(s=\(side))"
    }
    func area() -> Int {
        return side * side
    }
    func label() -> String {
        return "S\(side)"
    }
}

class Triangle: Drawable, Named {
    let base: Int
    let height: Int
    init(base: Int, height: Int) {
        self.base = base
        self.height = height
    }
    func draw() -> String {
        return "tri(b=\(base), h=\(height))"
    }
    func area() -> Int {
        return (base * height) / 2
    }
    func label() -> String {
        return "T\(base)x\(height)"
    }
}

class Scene {
    var items: [Drawable] = []
    func add(_ d: Drawable) {
        items.append(d)
    }
    func totalArea() -> Int {
        var t = 0
        for d in items {
            t += d.area()
        }
        return t
    }
    func render() {
        for d in items {
            print(d.draw())
        }
    }
}

let scene = Scene()
scene.add(Circle(radius: 2))
scene.add(Square(side: 3))
scene.add(Triangle(base: 4, height: 5))
scene.add(Circle(radius: 1))

print("== scene ==")
scene.render()
print("total area = \(scene.totalArea())")
print("item count = \(scene.items.count)")

let labels: [Named] = [
    Circle(radius: 7),
    Square(side: 2),
    Triangle(base: 1, height: 8)
]
for n in labels {
    print("label: \(n.label())")
}

