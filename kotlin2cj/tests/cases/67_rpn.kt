fun evalRpn(expr: String): Int {
    val stack = ArrayList<Int>()
    val tokens = expr.split(" ")
    for (tok in tokens) {
        if (tok in listOf("+", "-", "*", "/")) {
            val b = stack.removeAt(stack.size - 1)
            val a = stack.removeAt(stack.size - 1)
            val r = when (tok) {
                "+" -> a + b
                "-" -> a - b
                "*" -> a * b
                else -> a / b
            }
            stack.add(r)
        } else {
            stack.add(tok.toInt())
        }
    }
    return stack.last()
}

fun main() {
    println(evalRpn("3 4 +"))
    println(evalRpn("5 1 2 + 4 * + 3 -"))
    println(evalRpn("2 3 4 * +"))
}
