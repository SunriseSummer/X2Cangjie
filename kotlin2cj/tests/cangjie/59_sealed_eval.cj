open class Expr {}

class Lit <: Expr {
    let v: Int64
    init(v: Int64) {
        this.v = v
    }
}

class Add <: Expr {
    let l: Expr
    let r: Expr
    init(l: Expr, r: Expr) {
        this.l = l
        this.r = r
    }
}

class Mul <: Expr {
    let l: Expr
    let r: Expr
    init(l: Expr, r: Expr) {
        this.l = l
        this.r = r
    }
}

func eval(e: Expr): Int64 {
    return match (e) {
        case e: Lit => e.v
        case e: Add => eval(e.l) + eval(e.r)
        case e: Mul => eval(e.l) * eval(e.r)
        case _ => 0}
}

main() {
    let e: Expr = Add(Lit(2), Mul(Lit(3), Lit(4)))
    println(eval(e))
    let f: Expr = Mul(Add(Lit(1), Lit(2)), Lit(5))
    println(eval(f))
}
