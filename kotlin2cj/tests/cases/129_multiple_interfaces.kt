// Multiple interface implementation and method resolution
abstract class Shape {
    abstract fun area(): Double
    abstract fun name(): String
    override fun toString(): String {
        return "${name()}: area=${area()}"
    }
}

class Circle(val radius: Double) : Shape() {
    override fun area(): Double = 3.14159 * radius * radius
    override fun name(): String = "Circle"
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override fun area(): Double = width * height
    override fun name(): String = "Rectangle"
}

class Triangle(val base: Double, val h: Double) : Shape() {
    override fun area(): Double = 0.5 * base * h
    override fun name(): String = "Triangle"
}

fun largestShape(shapes: ArrayList<Shape>): Shape {
    var largest = shapes[0]
    for (s in shapes) {
        if (s.area() > largest.area()) {
            largest = s
        }
    }
    return largest
}

fun main() {
    val shapes = ArrayList<Shape>()
    shapes.add(Circle(5.0))
    shapes.add(Rectangle(4.0, 6.0))
    shapes.add(Triangle(8.0, 3.0))

    for (s in shapes) {
        println(s)
    }

    val biggest = largestShape(shapes)
    println("Largest: $biggest")

    // Polymorphic collection operations
    var totalArea = 0.0
    for (s in shapes) {
        totalArea += s.area()
    }
    println("Total area: $totalArea")
}
