package proj_shapes

import std.collection.*

open class Shape {
    let name: String
    init(name: String) {
        this.name = name
    }
    public open func area(): Float64 {
        return 0.0
    }
    public open func describe(): String {
        return "${name}: area=${area()}"
    }
}

class Circle <: Shape {
    let radius: Float64
    init(radius: Float64) {
        super("Circle")
        this.radius = radius
    }
    public override func area(): Float64 {
        return (3.14159 * radius) * radius
    }
    public override func describe(): String {
        return "Circle(r=${radius}): area=${area()}"
    }
}

class Rectangle <: Shape {
    let width: Float64
    let height: Float64
    init(width: Float64, height: Float64) {
        super("Rectangle")
        this.width = width
        this.height = height
    }
    public override func area(): Float64 {
        return width * height
    }
    public override func describe(): String {
        return "Rectangle(${width}x${height}): area=${area()}"
    }
}

class Triangle <: Shape {
    let base: Float64
    let height: Float64
    init(base: Float64, height: Float64) {
        super("Triangle")
        this.base = base
        this.height = height
    }
    public override func area(): Float64 {
        return (0.5 * base) * height
    }
    public override func describe(): String {
        return "Triangle(b=${base},h=${height}): area=${area()}"
    }
}
