// Recursive data structures: expression evaluator
class Expr(val kind: String, val value: Int, val left: Expr?, val right: Expr?)

fun makeNum(v: Int): Expr = Expr("num", v, null, null)
fun makeAdd(l: Expr, r: Expr): Expr = Expr("add", 0, l, r)
fun makeSub(l: Expr, r: Expr): Expr = Expr("sub", 0, l, r)
fun makeMul(l: Expr, r: Expr): Expr = Expr("mul", 0, l, r)

fun eval(e: Expr): Int {
    return when (e.kind) {
        "num" -> e.value
        "add" -> eval(e.left!!) + eval(e.right!!)
        "sub" -> eval(e.left!!) - eval(e.right!!)
        "mul" -> eval(e.left!!) * eval(e.right!!)
        else -> 0
    }
}

fun exprToString(e: Expr): String {
    return when (e.kind) {
        "num" -> e.value.toString()
        "add" -> "(${exprToString(e.left!!)} + ${exprToString(e.right!!)})"
        "sub" -> "(${exprToString(e.left!!)} - ${exprToString(e.right!!)})"
        "mul" -> "(${exprToString(e.left!!)} * ${exprToString(e.right!!)})"
        else -> "?"
    }
}

fun countNodes(e: Expr): Int {
    if (e.kind == "num") return 1
    return 1 + countNodes(e.left!!) + countNodes(e.right!!)
}

fun main() {
    // (2 + 3) * (4 - 1)
    val expr1 = makeMul(
        makeAdd(makeNum(2), makeNum(3)),
        makeSub(makeNum(4), makeNum(1))
    )
    println("${exprToString(expr1)} = ${eval(expr1)}")
    println("Nodes: ${countNodes(expr1)}")

    // 5 + (3 * 2)
    val expr2 = makeAdd(makeNum(5), makeMul(makeNum(3), makeNum(2)))
    println("${exprToString(expr2)} = ${eval(expr2)}")

    // Deep nesting: ((1+2)+(3+4))+((5+6)+(7+8))
    val deep = makeAdd(
        makeAdd(makeAdd(makeNum(1), makeNum(2)), makeAdd(makeNum(3), makeNum(4))),
        makeAdd(makeAdd(makeNum(5), makeNum(6)), makeAdd(makeNum(7), makeNum(8)))
    )
    println("${exprToString(deep)} = ${eval(deep)}")
    println("Nodes: ${countNodes(deep)}")
}
