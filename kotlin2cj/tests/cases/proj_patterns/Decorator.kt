interface Coffee {
    fun cost(): Int
    fun description(): String
}

class SimpleCoffee : Coffee {
    override fun cost(): Int = 5
    override fun description(): String = "Simple coffee"
}

class MilkDecorator(val inner: Coffee) : Coffee {
    override fun cost(): Int = inner.cost() + 2
    override fun description(): String = inner.description() + " + milk"
}

class SugarDecorator(val inner: Coffee) : Coffee {
    override fun cost(): Int = inner.cost() + 1
    override fun description(): String = inner.description() + " + sugar"
}

class WhipDecorator(val inner: Coffee) : Coffee {
    override fun cost(): Int = inner.cost() + 3
    override fun description(): String = inner.description() + " + whip"
}

fun buildCoffee(addMilk: Boolean, addSugar: Boolean, addWhip: Boolean): Coffee {
    var coffee: Coffee = SimpleCoffee()
    if (addMilk) coffee = MilkDecorator(coffee)
    if (addSugar) coffee = SugarDecorator(coffee)
    if (addWhip) coffee = WhipDecorator(coffee)
    return coffee
}
