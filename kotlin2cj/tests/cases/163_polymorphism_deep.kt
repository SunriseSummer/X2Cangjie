// Test: Complex class hierarchy with abstract methods, interface, and polymorphism
interface Describable {
    fun describe(): String
}

abstract class Shape : Describable {
    abstract fun area(): Double
    abstract fun perimeter(): Double
    override fun describe(): String = "Shape(area=${area()}, perimeter=${perimeter()})"
}

class Circle(val radius: Double) : Shape() {
    override fun area(): Double = 3.14159 * radius * radius
    override fun perimeter(): Double = 2.0 * 3.14159 * radius
    override fun describe(): String = "Circle(r=$radius, area=${area()})"
}

class Rect(val width: Double, val height: Double) : Shape() {
    override fun area(): Double = width * height
    override fun perimeter(): Double = 2.0 * (width + height)
    override fun describe(): String = "Rect(${width}x${height}, area=${area()})"
}

class Triangle(val a: Double, val b: Double, val c: Double) : Shape() {
    override fun area(): Double {
        val s = (a + b + c) / 2.0
        var prod = s * (s - a) * (s - b) * (s - c)
        if (prod < 0.0) prod = 0.0
        // Simple sqrt approximation via Newton's method
        var x = prod
        if (x > 0.0) {
            for (i in 0..19) {
                x = (x + prod / x) / 2.0
            }
        }
        return x
    }
    override fun perimeter(): Double = a + b + c
}

fun printShapes(shapes: ArrayList<Shape>) {
    for (s in shapes) {
        println(s.describe())
    }
}

fun totalArea(shapes: ArrayList<Shape>): Double {
    var sum = 0.0
    for (s in shapes) {
        sum += s.area()
    }
    return sum
}

fun main() {
    val shapes = ArrayList<Shape>()
    shapes.add(Circle(5.0))
    shapes.add(Rect(3.0, 4.0))
    shapes.add(Triangle(3.0, 4.0, 5.0))

    printShapes(shapes)
    println("Total area: ${totalArea(shapes)}")
    println("Count: ${shapes.size}")
}
