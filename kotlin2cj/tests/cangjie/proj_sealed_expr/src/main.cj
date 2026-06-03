package proj_sealed_expr

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
