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

main() {
    let e1: Expr = Mul(Add(Num(2), Num(3)), Num(4))
    println("${stringify(e1)} = ${eval(e1)}")
    let e2: Expr = Neg(Add(Num(5), Num(3)))
    println("${stringify(e2)} = ${eval(e2)}")
    let e3: Expr = Add(Num(1), Mul(Num(2), Add(Num(3), Num(4))))
    println("${stringify(e3)} = ${eval(e3)}")
    let e4: Expr = Neg(Mul(Num(2), Neg(Num(3))))
    println("${stringify(e4)} = ${eval(e4)}")
    let e5: Expr = Add(Add(Num(10), Num(20)), Add(Num(30), Num(40)))
    println("${stringify(e5)} = ${eval(e5)}")
}