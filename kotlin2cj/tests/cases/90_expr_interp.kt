// Generalization probe 2: expression tree + interpreter using sealed hierarchy.
abstract class Expr {
    abstract fun eval(): Int
    abstract fun show(): String
}

class Num(val value: Int) : Expr() {
    override fun eval(): Int = value
    override fun show(): String = value.toString()
}

class Add(val left: Expr, val right: Expr) : Expr() {
    override fun eval(): Int = left.eval() + right.eval()
    override fun show(): String = "(${left.show()} + ${right.show()})"
}

class Mul(val left: Expr, val right: Expr) : Expr() {
    override fun eval(): Int = left.eval() * right.eval()
    override fun show(): String = "(${left.show()} * ${right.show()})"
}

class Neg(val inner: Expr) : Expr() {
    override fun eval(): Int = -inner.eval()
    override fun show(): String = "-${inner.show()}"
}

fun depth(e: Expr): Int = when (e) {
    is Num -> 1
    is Add -> 1 + maxOf(depth(e.left), depth(e.right))
    is Mul -> 1 + maxOf(depth(e.left), depth(e.right))
    is Neg -> 1 + depth(e.inner)
    else -> 0
}

class Stack<T> {
    val items = ArrayList<T>()
    fun push(x: T) { items.add(x) }
    fun pop(): T {
        val x = items[items.size - 1]
        items.removeAt(items.size - 1)
        return x
    }
    fun isEmpty(): Boolean = items.isEmpty()
    fun size(): Int = items.size
}

fun main() {
    val e = Add(Mul(Num(3), Num(4)), Neg(Num(5)))
    println("Expr: ${e.show()}")
    println("Eval: ${e.eval()}")
    println("Depth: ${depth(e)}")

    val exprs = ArrayList<Expr>()
    exprs.add(Num(7))
    exprs.add(Add(Num(1), Num(2)))
    exprs.add(Mul(Add(Num(2), Num(3)), Num(4)))
    exprs.add(Neg(Add(Num(10), Num(5))))

    println("=== Batch eval ===")
    var sum = 0
    for (ex in exprs) {
        val v = ex.eval()
        sum = sum + v
        println("${ex.show()} = $v")
    }
    println("Sum of all: $sum")

    val values = exprs.map { it.eval() }
    println("Sorted values: ${values.sorted().joinToString(", ")}")
    println("Max: ${values.maxOrNull() ?: 0}")

    println("=== Generic Stack ===")
    val st = Stack<Int>()
    for (i in 1..5) {
        st.push(i * i)
    }
    val drained = ArrayList<Int>()
    while (!st.isEmpty()) {
        drained.add(st.pop())
    }
    println("Drained (LIFO): ${drained.joinToString(" ")}")

    val names = Stack<String>()
    names.push("alpha")
    names.push("beta")
    names.push("gamma")
    println("Top: ${names.pop()}, remaining: ${names.size()}")

    println("=== Counting by depth ===")
    val depths = exprs.map { depth(it) }
    var maxD = 0
    for (d in depths) {
        if (d > maxD) {
            maxD = d
        }
    }
    for (level in 1..maxD) {
        var c = 0
        for (d in depths) {
            if (d == level) {
                c = c + 1
            }
        }
        println("depth $level: $c expr(s)")
    }
}
