fun main() {
    // (2 + 3) * 4 = 20
    val e1: Expr = Mul(Add(Num(2), Num(3)), Num(4))
    println("${stringify(e1)} = ${eval(e1)}")

    // -(5 + 3) = -8
    val e2: Expr = Neg(Add(Num(5), Num(3)))
    println("${stringify(e2)} = ${eval(e2)}")

    // 1 + (2 * (3 + 4)) = 15
    val e3: Expr = Add(Num(1), Mul(Num(2), Add(Num(3), Num(4))))
    println("${stringify(e3)} = ${eval(e3)}")

    // -(2 * -(3)) = 6
    val e4: Expr = Neg(Mul(Num(2), Neg(Num(3))))
    println("${stringify(e4)} = ${eval(e4)}")

    // (10 + 20) + (30 + 40) = 100
    val e5: Expr = Add(Add(Num(10), Num(20)), Add(Num(30), Num(40)))
    println("${stringify(e5)} = ${eval(e5)}")
}
