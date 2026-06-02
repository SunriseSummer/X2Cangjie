interface Strategy {
    fun execute(a: Int, b: Int): Int
    fun name(): String
}

class AddStrategy : Strategy {
    override fun execute(a: Int, b: Int): Int = a + b
    override fun name(): String = "Add"
}

class SubtractStrategy : Strategy {
    override fun execute(a: Int, b: Int): Int = a - b
    override fun name(): String = "Subtract"
}

class MultiplyStrategy : Strategy {
    override fun execute(a: Int, b: Int): Int = a * b
    override fun name(): String = "Multiply"
}

class Calculator {
    private var strategy: Strategy = AddStrategy()

    fun setStrategy(s: Strategy) {
        strategy = s
    }

    fun calculate(a: Int, b: Int): Int {
        return strategy.execute(a, b)
    }

    fun currentStrategy(): String {
        return strategy.name()
    }
}
