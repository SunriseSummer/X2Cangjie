enum class Op { ADD, SUB, MUL }
fun apply(op: Op, a: Int, b: Int): Int = when (op) {
    Op.ADD -> a + b
    Op.SUB -> a - b
    Op.MUL -> a * b
}
fun main() {
    val ops = listOf(Op.ADD, Op.SUB, Op.MUL)
    for (op in ops) {
        println("$op: ${apply(op, 6, 4)}")
    }
    val results = ops.map { apply(it, 10, 3) }
    println("sum=${results.sum()}")
}
