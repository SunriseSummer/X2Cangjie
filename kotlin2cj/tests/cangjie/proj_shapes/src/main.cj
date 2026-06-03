package proj_shapes

import std.collection.*

func printShapeInfo(shape: Shape) {
    println(shape.describe())
}

main() {
    let shapes = ArrayList<Shape>()
    shapes.add(Circle(5.0))
    shapes.add(Rectangle(4.0, 6.0))
    shapes.add(Triangle(3.0, 8.0))
    for (s in shapes) {
        printShapeInfo(s)
    }
    println("Total shapes: ${shapes.size}")
}
