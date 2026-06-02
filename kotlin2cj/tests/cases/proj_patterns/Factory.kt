interface Shape {
    fun area(): Int
    fun perimeter(): Int
    fun describe(): String
}

class Circle(val radius: Int) : Shape {
    override fun area(): Int = 314 * radius * radius / 100
    override fun perimeter(): Int = 628 * radius / 100
    override fun describe(): String = "Circle(radius=$radius)"
}

class Rectangle(val width: Int, val height: Int) : Shape {
    override fun area(): Int = width * height
    override fun perimeter(): Int = 2 * (width + height)
    override fun describe(): String = "Rectangle(width=$width, height=$height)"
}

class Triangle(val base: Int, val triangleHeight: Int, val side1: Int, val side2: Int) : Shape {
    override fun area(): Int = base * triangleHeight / 2
    override fun perimeter(): Int = base + side1 + side2
    override fun describe(): String = "Triangle(base=$base, height=$triangleHeight)"
}

fun createShape(shapeType: String, param1: Int, param2: Int, param3: Int, param4: Int): Shape? {
    return when (shapeType) {
        "circle" -> Circle(param1)
        "rectangle" -> Rectangle(param1, param2)
        "triangle" -> Triangle(param1, param2, param3, param4)
        else -> null
    }
}
