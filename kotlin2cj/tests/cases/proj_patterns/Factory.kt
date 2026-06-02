interface Shape {
    fun name(): String
    fun area(): Int
    fun perimeter(): Int
    fun describe(): String
    fun scale(factor: Int): Shape
}

data class ShapeSpec(
    val type: String,
    val first: Int,
    val second: Int = 0,
    val third: Int = 0
)

class Circle(val radius: Int) : Shape {
    override fun name(): String = "Circle"

    override fun area(): Int = radius * radius * 3

    override fun perimeter(): Int = radius * 6

    override fun describe(): String {
        return "Circle(radius=$radius, area=${area()}, perimeter=${perimeter()})"
    }

    override fun scale(factor: Int): Shape = Circle(radius * factor)
}

class Rectangle(val width: Int, val height: Int) : Shape {
    override fun name(): String = "Rectangle"

    override fun area(): Int = width * height

    override fun perimeter(): Int = (width + height) * 2

    override fun describe(): String {
        return "Rectangle(width=$width, height=$height, area=${area()}, perimeter=${perimeter()})"
    }

    override fun scale(factor: Int): Shape = Rectangle(width * factor, height * factor)
}

class Triangle(val base: Int, val height: Int, val side: Int) : Shape {
    override fun name(): String = "Triangle"

    override fun area(): Int = base * height / 2

    override fun perimeter(): Int = base + side + side

    override fun describe(): String {
        return "Triangle(base=$base, height=$height, side=$side, area=${area()}, perimeter=${perimeter()})"
    }

    override fun scale(factor: Int): Shape = Triangle(base * factor, height * factor, side * factor)
}

open class ShapeFactory {
    open fun createShape(type: String, first: Int, second: Int = 0, third: Int = 0): Shape? {
        return when (type.manualLower()) {
            "circle" -> Circle(first)
            "rectangle" -> Rectangle(first, second)
            "triangle" -> Triangle(first, second, third)
            else -> null
        }
    }

    fun createBatch(specs: MutableList<ShapeSpec>): MutableList<Shape> {
        val shapes = mutableListOf<Shape>()
        for (spec in specs) {
            val shape = createShape(spec.type, spec.first, spec.second, spec.third)
            if (shape != null) {
                shapes.add(shape)
            }
        }
        return shapes
    }

    fun totalArea(shapes: MutableList<Shape>): Int {
        var sum = 0
        for (shape in shapes) {
            sum += shape.area()
        }
        return sum
    }

    fun totalPerimeter(shapes: MutableList<Shape>): Int {
        var sum = 0
        for (shape in shapes) {
            sum += shape.perimeter()
        }
        return sum
    }

    companion object {
        fun standardSpecs(): MutableList<ShapeSpec> {
            return mutableListOf(
                ShapeSpec("circle", 3),
                ShapeSpec("rectangle", 4, 5),
                ShapeSpec("triangle", 6, 4, 5)
            )
        }
    }
}

data class ColoredShape(val color: String, val shape: Shape) {
    fun describe(): String {
        return "$color ${shape.describe()}"
    }

    fun tag(): String {
        return "${color.manualUpper()}-${shape.name().manualUpper()}"
    }
}

interface AbstractShapeFactory {
    fun paletteName(): String
    fun createPrimaryShape(): ColoredShape
    fun createAccentShape(): ColoredShape
    fun createNeutralShape(): ColoredShape
}

class ColoredShapeFactory(val color: String) : ShapeFactory(), AbstractShapeFactory {
    override fun paletteName(): String {
        return "$color-theme"
    }

    fun createColoredShape(type: String, first: Int, second: Int = 0, third: Int = 0): ColoredShape? {
        val shape = createShape(type, first, second, third)
        return if (shape == null) {
            null
        } else {
            ColoredShape(color, shape)
        }
    }

    override fun createPrimaryShape(): ColoredShape {
        return when (color.manualLower()) {
            "red" -> ColoredShape(color, Circle(4))
            "blue" -> ColoredShape(color, Rectangle(5, 2))
            else -> ColoredShape(color, Triangle(6, 4, 5))
        }
    }

    override fun createAccentShape(): ColoredShape {
        return when (color.manualLower()) {
            "red" -> ColoredShape(color, Rectangle(3, 6))
            "blue" -> ColoredShape(color, Triangle(5, 4, 4))
            else -> ColoredShape(color, Circle(2))
        }
    }

    override fun createNeutralShape(): ColoredShape {
        return ColoredShape("gray", Rectangle(2, 2))
    }

    fun buildShowcase(): MutableList<ColoredShape> {
        val list = mutableListOf<ColoredShape>()
        list.add(createPrimaryShape())
        list.add(createAccentShape())
        list.add(createNeutralShape())
        return list
    }

    fun summary(shapes: MutableList<ColoredShape>): String {
        val parts = mutableListOf<String>()
        for (shape in shapes) {
            parts.add(shape.tag())
        }
        return parts.joinToString(", ")
    }
}
