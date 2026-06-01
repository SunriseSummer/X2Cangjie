open class Shape(val name: String) {
    open fun area(): Double = 0.0
    open fun describe(): String = "$name: area=${area()}"
}

class Circle(val radius: Double) : Shape("Circle") {
    override fun area(): Double = 3.14159 * radius * radius
    override fun describe(): String = "Circle(r=$radius): area=${area()}"
}

class Rectangle(val width: Double, val height: Double) : Shape("Rectangle") {
    override fun area(): Double = width * height
    override fun describe(): String = "Rectangle(${width}x${height}): area=${area()}"
}

class Triangle(val base: Double, val height: Double) : Shape("Triangle") {
    override fun area(): Double = 0.5 * base * height
    override fun describe(): String = "Triangle(b=$base,h=$height): area=${area()}"
}
