import std.collection.*

interface Describable {
    func describe(): String
}

abstract class Shape <: Describable {
    public func area(): Float64
    public func perimeter(): Float64
    public open override func describe(): String {
        return "Shape(area=${area()}, perimeter=${perimeter()})"
    }
}

class Circle <: Shape {
    let radius: Float64
    init(radius: Float64) {
        this.radius = radius
    }
    public override func area(): Float64 {
        return (3.14159 * radius) * radius
    }
    public override func perimeter(): Float64 {
        return (2.0 * 3.14159) * radius
    }
    public override func describe(): String {
        return "Circle(r=${radius}, area=${area()})"
    }
}

class Rect <: Shape {
    let width: Float64
    let height: Float64
    init(width: Float64, height: Float64) {
        this.width = width
        this.height = height
    }
    public override func area(): Float64 {
        return width * height
    }
    public override func perimeter(): Float64 {
        return 2.0 * Float64((width + height))
    }
    public override func describe(): String {
        return "Rect(${width}x${height}, area=${area()})"
    }
}

class Triangle <: Shape {
    let a: Float64
    let b: Float64
    let c: Float64
    init(a: Float64, b: Float64, c: Float64) {
        this.a = a
        this.b = b
        this.c = c
    }
    public override func area(): Float64 {
        let s = Float64(((a + b) + c)) / 2.0
        var prod = ((s * (s - a)) * (s - b)) * (s - c)
        if (prod < 0.0) {
            prod = 0.0
        }
        var x = prod
        if (x > 0.0) {
            for (i in 0..=19) {
                x = (x + (prod / x)) / 2.0
            }
        }
        return x
    }
    public override func perimeter(): Float64 {
        return (a + b) + c
    }
}

func printShapes(shapes: ArrayList<Shape>) {
    for (s in shapes) {
        println(s.describe())
    }
}

func totalArea(shapes: ArrayList<Shape>): Float64 {
    var sum = 0.0
    for (s in shapes) {
        sum += s.area()
    }
    return sum
}

main() {
    let shapes = ArrayList<Shape>()
    shapes.add(Circle(5.0))
    shapes.add(Rect(3.0, 4.0))
    shapes.add(Triangle(3.0, 4.0, 5.0))
    printShapes(shapes)
    println("Total area: ${totalArea(shapes)}")
    println("Count: ${shapes.size}")
}
