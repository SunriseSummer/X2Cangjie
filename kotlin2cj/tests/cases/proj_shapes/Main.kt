fun printShapeInfo(shape: Shape) {
    println(shape.describe())
}

fun main() {
    val shapes = mutableListOf<Shape>()
    shapes.add(Circle(5.0))
    shapes.add(Rectangle(4.0, 6.0))
    shapes.add(Triangle(3.0, 8.0))

    for (s in shapes) {
        printShapeInfo(s)
    }

    println("Total shapes: ${shapes.size}")
}
