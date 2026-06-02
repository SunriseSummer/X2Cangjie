class Expr {
    let kind: String
    let value: Int64
    let left: ?Expr
    let right: ?Expr
    init(kind: String, value: Int64, left: ?Expr, right: ?Expr) {
        this.kind = kind
        this.value = value
        this.left = left
        this.right = right
    }
}

func makeNum(v: Int64): Expr {
    return Expr("num", v, None, None)
}

func makeAdd(l: Expr, r: Expr): Expr {
    return Expr("add", 0, l, r)
}

func makeSub(l: Expr, r: Expr): Expr {
    return Expr("sub", 0, l, r)
}

func makeMul(l: Expr, r: Expr): Expr {
    return Expr("mul", 0, l, r)
}

func eval(e: Expr): Int64 {
    return match (e.kind) {
        case "num" => e.value
        case "add" => eval(e.left.getOrThrow()) + eval(e.right.getOrThrow())
        case "sub" => eval(e.left.getOrThrow()) - eval(e.right.getOrThrow())
        case "mul" => eval(e.left.getOrThrow()) * eval(e.right.getOrThrow())
        case _ => 0}
}

func exprToString(e: Expr): String {
    return match (e.kind) {
        case "num" => e.value.toString()
        case "add" => "(${exprToString(e.left.getOrThrow())} + ${exprToString(e.right.getOrThrow())})"
        case "sub" => "(${exprToString(e.left.getOrThrow())} - ${exprToString(e.right.getOrThrow())})"
        case "mul" => "(${exprToString(e.left.getOrThrow())} * ${exprToString(e.right.getOrThrow())})"
        case _ => "?"}
}

func countNodes(e: Expr): Int64 {
    if (e.kind == "num") {
        return 1
    }
    return (1 + countNodes(e.left.getOrThrow())) + countNodes(e.right.getOrThrow())
}

main() {
    let expr1 = makeMul(makeAdd(makeNum(2), makeNum(3)), makeSub(makeNum(4), makeNum(1)))
    println("${exprToString(expr1)} = ${eval(expr1)}")
    println("Nodes: ${countNodes(expr1)}")
    let expr2 = makeAdd(makeNum(5), makeMul(makeNum(3), makeNum(2)))
    println("${exprToString(expr2)} = ${eval(expr2)}")
    let deep = makeAdd(makeAdd(makeAdd(makeNum(1), makeNum(2)), makeAdd(makeNum(3), makeNum(4))), makeAdd(makeAdd(makeNum(5), makeNum(6)), makeAdd(makeNum(7), makeNum(8))))
    println("${exprToString(deep)} = ${eval(deep)}")
    println("Nodes: ${countNodes(deep)}")
}
