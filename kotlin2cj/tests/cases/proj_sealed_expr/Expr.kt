sealed class Expr
class Num(val value: Int) : Expr()
class Add(val left: Expr, val right: Expr) : Expr()
class Mul(val left: Expr, val right: Expr) : Expr()
class Neg(val expr: Expr) : Expr()

fun eval(e: Expr): Int = when (e) {
    is Num -> e.value
    is Add -> eval(e.left) + eval(e.right)
    is Mul -> eval(e.left) * eval(e.right)
    is Neg -> -eval(e.expr)
    else -> 0
}

fun stringify(e: Expr): String = when (e) {
    is Num -> "${e.value}"
    is Add -> "(${stringify(e.left)} + ${stringify(e.right)})"
    is Mul -> "(${stringify(e.left)} * ${stringify(e.right)})"
    is Neg -> "(-${stringify(e.expr)})"
    else -> "?"
}
