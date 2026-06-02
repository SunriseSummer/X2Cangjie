sealed class Expr {
    abstract fun acceptEval(visitor: EvalVisitor): Int
    abstract fun acceptPrint(visitor: PrintVisitor): String
    abstract fun acceptSimplify(visitor: SimplifyVisitor): Expr
}

data class NumberExpr(val value: Int) : Expr() {
    override fun acceptEval(visitor: EvalVisitor): Int = visitor.visitNumber(this)
    override fun acceptPrint(visitor: PrintVisitor): String = visitor.visitNumber(this)
    override fun acceptSimplify(visitor: SimplifyVisitor): Expr = visitor.visitNumber(this)
}

data class AddExpr(val left: Expr, val right: Expr) : Expr() {
    override fun acceptEval(visitor: EvalVisitor): Int = visitor.visitAdd(this)
    override fun acceptPrint(visitor: PrintVisitor): String = visitor.visitAdd(this)
    override fun acceptSimplify(visitor: SimplifyVisitor): Expr = visitor.visitAdd(this)
}

data class SubExpr(val left: Expr, val right: Expr) : Expr() {
    override fun acceptEval(visitor: EvalVisitor): Int = visitor.visitSub(this)
    override fun acceptPrint(visitor: PrintVisitor): String = visitor.visitSub(this)
    override fun acceptSimplify(visitor: SimplifyVisitor): Expr = visitor.visitSub(this)
}

data class MulExpr(val left: Expr, val right: Expr) : Expr() {
    override fun acceptEval(visitor: EvalVisitor): Int = visitor.visitMul(this)
    override fun acceptPrint(visitor: PrintVisitor): String = visitor.visitMul(this)
    override fun acceptSimplify(visitor: SimplifyVisitor): Expr = visitor.visitMul(this)
}

class EvalVisitor {
    fun visitNumber(expr: NumberExpr): Int = expr.value

    fun visitAdd(expr: AddExpr): Int {
        return expr.left.acceptEval(this) + expr.right.acceptEval(this)
    }

    fun visitSub(expr: SubExpr): Int {
        return expr.left.acceptEval(this) - expr.right.acceptEval(this)
    }

    fun visitMul(expr: MulExpr): Int {
        return expr.left.acceptEval(this) * expr.right.acceptEval(this)
    }
}

class PrintVisitor {
    fun visitNumber(expr: NumberExpr): String = "${expr.value}"

    fun visitAdd(expr: AddExpr): String {
        return "(${expr.left.acceptPrint(this)} + ${expr.right.acceptPrint(this)})"
    }

    fun visitSub(expr: SubExpr): String {
        return "(${expr.left.acceptPrint(this)} - ${expr.right.acceptPrint(this)})"
    }

    fun visitMul(expr: MulExpr): String {
        return "(${expr.left.acceptPrint(this)} * ${expr.right.acceptPrint(this)})"
    }
}

class SimplifyVisitor {
    fun visitNumber(expr: NumberExpr): Expr = expr

    fun visitAdd(expr: AddExpr): Expr {
        val left = expr.left.acceptSimplify(this)
        val right = expr.right.acceptSimplify(this)
        if (left is NumberExpr && right is NumberExpr) {
            return NumberExpr(left.value + right.value)
        }
        if (left is NumberExpr && left.value == 0) {
            return right
        }
        if (right is NumberExpr && right.value == 0) {
            return left
        }
        return AddExpr(left, right)
    }

    fun visitSub(expr: SubExpr): Expr {
        val left = expr.left.acceptSimplify(this)
        val right = expr.right.acceptSimplify(this)
        if (left is NumberExpr && right is NumberExpr) {
            return NumberExpr(left.value - right.value)
        }
        if (right is NumberExpr && right.value == 0) {
            return left
        }
        return SubExpr(left, right)
    }

    fun visitMul(expr: MulExpr): Expr {
        val left = expr.left.acceptSimplify(this)
        val right = expr.right.acceptSimplify(this)
        if (left is NumberExpr && right is NumberExpr) {
            return NumberExpr(left.value * right.value)
        }
        if (left is NumberExpr && left.value == 0) {
            return NumberExpr(0)
        }
        if (right is NumberExpr && right.value == 0) {
            return NumberExpr(0)
        }
        if (left is NumberExpr && left.value == 1) {
            return right
        }
        if (right is NumberExpr && right.value == 1) {
            return left
        }
        return MulExpr(left, right)
    }
}

fun summarizeExpression(expr: Expr): String {
    val eval = EvalVisitor()
    val printer = PrintVisitor()
    val simplifier = SimplifyVisitor()
    val simplified = expr.acceptSimplify(simplifier)
    return "expr=${expr.acceptPrint(printer)} value=${expr.acceptEval(eval)} simplified=${simplified.acceptPrint(printer)} simplifiedValue=${simplified.acceptEval(eval)}"
}
