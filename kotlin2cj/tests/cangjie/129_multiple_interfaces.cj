import std.collection.*

abstract class Shape <: ToString {
    public func area(): Float64
    public func name(): String
    public open override func toString(): String {
        return "${name()}: area=${area()}"
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
    public override func name(): String {
        return "Circle"
    }
}

class Rectangle <: Shape {
    let width: Float64
    let height: Float64
    init(width: Float64, height: Float64) {
        this.width = width
        this.height = height
    }
    public override func area(): Float64 {
        return width * height
    }
    public override func name(): String {
        return "Rectangle"
    }
}

class Triangle <: Shape {
    let base: Float64
    let h: Float64
    init(base: Float64, h: Float64) {
        this.base = base
        this.h = h
    }
    public override func area(): Float64 {
        return (0.5 * base) * h
    }
    public override func name(): String {
        return "Triangle"
    }
}

func largestShape(shapes: ArrayList<Shape>): Shape {
    var largest = shapes[0]
    for (s in shapes) {
        if (s.area() > largest.area()) {
            largest = s
        }
    }
    return largest
}

main() {
    let shapes = ArrayList<Shape>()
    shapes.add(Circle(5.0))
    shapes.add(Rectangle(4.0, 6.0))
    shapes.add(Triangle(8.0, 3.0))
    for (s in shapes) {
        println(s)
    }
    let biggest = largestShape(shapes)
    println("Largest: ${biggest}")
    var totalArea = 0.0
    for (s in shapes) {
        totalArea += s.area()
    }
    println("Total area: ${totalArea}")
}
