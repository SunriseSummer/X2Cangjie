interface Coffee {
    fun cost(): Int
    fun description(): String
    fun ingredients(): MutableList<String>
}

class SimpleCoffee(val bean: String = "House Blend") : Coffee {
    override fun cost(): Int = 5

    override fun description(): String = "$bean coffee"

    override fun ingredients(): MutableList<String> {
        return mutableListOf(bean, "water")
    }
}

abstract class CoffeeDecorator(val inner: Coffee) : Coffee {
    override fun ingredients(): MutableList<String> {
        val items = mutableListOf<String>()
        for (item in inner.ingredients()) {
            items.add(item)
        }
        return items
    }
}

class MilkDecorator(inner: Coffee, val shots: Int = 1) : CoffeeDecorator(inner) {
    override fun cost(): Int = inner.cost() + (shots * 2)

    override fun description(): String = inner.description() + " + milk x$shots"

    override fun ingredients(): MutableList<String> {
        val items = super.ingredients()
        var i = 0
        while (i < shots) {
            items.add("milk")
            i += 1
        }
        return items
    }
}

class SugarDecorator(inner: Coffee, val cubes: Int = 1) : CoffeeDecorator(inner) {
    override fun cost(): Int = inner.cost() + cubes

    override fun description(): String = inner.description() + " + sugar x$cubes"

    override fun ingredients(): MutableList<String> {
        val items = super.ingredients()
        var i = 0
        while (i < cubes) {
            items.add("sugar")
            i += 1
        }
        return items
    }
}

class WhipDecorator(inner: Coffee, val layers: Int = 1) : CoffeeDecorator(inner) {
    override fun cost(): Int = inner.cost() + (layers * 3)

    override fun description(): String = inner.description() + " + whip x$layers"

    override fun ingredients(): MutableList<String> {
        val items = super.ingredients()
        var i = 0
        while (i < layers) {
            items.add("whip")
            i += 1
        }
        return items
    }
}

class CoffeeBuilder(baseBean: String = "House Blend") {
    private var current: Coffee = SimpleCoffee(baseBean)

    fun addMilk(shots: Int = 1): CoffeeBuilder {
        current = MilkDecorator(current, shots)
        return this
    }

    fun addSugar(cubes: Int = 1): CoffeeBuilder {
        current = SugarDecorator(current, cubes)
        return this
    }

    fun addWhip(layers: Int = 1): CoffeeBuilder {
        current = WhipDecorator(current, layers)
        return this
    }

    fun build(): Coffee {
        return current
    }
}

fun coffeeReceiptLines(coffee: Coffee): MutableList<String> {
    val lines = mutableListOf<String>()
    lines.add("drink=${coffee.description()}")
    lines.add("cost=${coffee.cost()}")
    val ingredientText = coffee.ingredients().joinToString(", ")
    lines.add("ingredients=$ingredientText")
    return lines
}
