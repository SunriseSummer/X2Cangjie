sealed class Expr
class Lit(val v: Int) : Expr()
class Add(val l: Expr, val r: Expr) : Expr()
class Mul(val l: Expr, val r: Expr) : Expr()

fun eval(e: Expr): Int = when (e) {
    is Lit -> e.v
    is Add -> eval(e.l) + eval(e.r)
    is Mul -> eval(e.l) * eval(e.r)
    else -> 0
}

fun main() {
    val e: Expr = Add(Lit(2), Mul(Lit(3), Lit(4)))
    println(eval(e))
    val f: Expr = Mul(Add(Lit(1), Lit(2)), Lit(5))
    println(eval(f))
}
