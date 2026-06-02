package proj_patterns

import std.collection.*
import std.deriving.*

interface Shape {
    func area(): Int64
    func perimeter(): Int64
    func describe(): String
}

class Circle <: Shape {
    let radius: Int64
    init(radius: Int64) {
        this.radius = radius
    }
    public override func area(): Int64 {
        return ((314 * radius) * radius) / 100
    }
    public override func perimeter(): Int64 {
        return (628 * radius) / 100
    }
    public override func describe(): String {
        return "Circle(radius=${radius})"
    }
}

class Rectangle <: Shape {
    let width: Int64
    let height: Int64
    init(width: Int64, height: Int64) {
        this.width = width
        this.height = height
    }
    public override func area(): Int64 {
        return width * height
    }
    public override func perimeter(): Int64 {
        return 2 * (width + height)
    }
    public override func describe(): String {
        return "Rectangle(width=${width}, height=${height})"
    }
}

class Triangle <: Shape {
    let base: Int64
    let triangleHeight: Int64
    let side1: Int64
    let side2: Int64
    init(base: Int64, triangleHeight: Int64, side1: Int64, side2: Int64) {
        this.base = base
        this.triangleHeight = triangleHeight
        this.side1 = side1
        this.side2 = side2
    }
    public override func area(): Int64 {
        return (base * triangleHeight) / 2
    }
    public override func perimeter(): Int64 {
        return (base + side1) + side2
    }
    public override func describe(): String {
        return "Triangle(base=${base}, height=${triangleHeight})"
    }
}

func createShape(shapeType: String, param1: Int64, param2: Int64, param3: Int64, param4: Int64): ?Shape {
    return match (shapeType) {
        case "circle" => Circle(param1)
        case "rectangle" => Rectangle(param1, param2)
        case "triangle" => Triangle(param1, param2, param3, param4)
        case _ => None}
}
