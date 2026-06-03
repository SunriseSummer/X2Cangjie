package proj_sealed_expr

open class Expr {}

class Num <: Expr {
    let value: Int64
    init(value: Int64) {
        this.value = value
    }
}

class Add <: Expr {
    let left: Expr
    let right: Expr
    init(left: Expr, right: Expr) {
        this.left = left
        this.right = right
    }
}

class Mul <: Expr {
    let left: Expr
    let right: Expr
    init(left: Expr, right: Expr) {
        this.left = left
        this.right = right
    }
}

class Neg <: Expr {
    let expr: Expr
    init(expr: Expr) {
        this.expr = expr
    }
}

func eval(e: Expr): Int64 {
    return match (e) {
        case e: Num => e.value
        case e: Add => eval(e.left) + eval(e.right)
        case e: Mul => eval(e.left) * eval(e.right)
        case e: Neg => -eval(e.expr)
        case _ => 0}
}

func stringify(e: Expr): String {
    return match (e) {
        case e: Num => "${e.value}"
        case e: Add => "(${stringify(e.left)} + ${stringify(e.right)})"
        case e: Mul => "(${stringify(e.left)} * ${stringify(e.right)})"
        case e: Neg => "(-${stringify(e.expr)})"
        case _ => "?"}
}
