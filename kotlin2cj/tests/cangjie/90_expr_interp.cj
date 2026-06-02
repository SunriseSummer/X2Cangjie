import std.collection.*
import std.sort.*

abstract class Expr {
    public func eval(): Int64
    public func show(): String
}

class Num <: Expr {
    let value: Int64
    init(value: Int64) {
        this.value = value
    }
    public override func eval(): Int64 {
        return value
    }
    public override func show(): String {
        return value.toString()
    }
}

class Add <: Expr {
    let left: Expr
    let right: Expr
    init(left: Expr, right: Expr) {
        this.left = left
        this.right = right
    }
    public override func eval(): Int64 {
        return left.eval() + right.eval()
    }
    public override func show(): String {
        return "(${left.show()} + ${right.show()})"
    }
}

class Mul <: Expr {
    let left: Expr
    let right: Expr
    init(left: Expr, right: Expr) {
        this.left = left
        this.right = right
    }
    public override func eval(): Int64 {
        return left.eval() * right.eval()
    }
    public override func show(): String {
        return "(${left.show()} * ${right.show()})"
    }
}

class Neg <: Expr {
    let inner: Expr
    init(inner: Expr) {
        this.inner = inner
    }
    public override func eval(): Int64 {
        return -inner.eval()
    }
    public override func show(): String {
        return "-${inner.show()}"
    }
}

func depth(e: Expr): Int64 {
    return match (e) {
        case e: Num => 1
        case e: Add => 1 + (if (depth(e.left) > depth(e.right)) { depth(e.left) } else { depth(e.right) })
        case e: Mul => 1 + (if (depth(e.left) > depth(e.right)) { depth(e.left) } else { depth(e.right) })
        case e: Neg => 1 + depth(e.inner)
        case _ => 0}
}

class Stack<T> {
    let items = ArrayList<T>()
    func push(x: T) {
        items.add(x)
    }
    func pop(): T {
        let x = items[items.size - 1]
        items.remove(at: items.size - 1)
        return x
    }
    func isEmpty(): Bool {
        return items.isEmpty()
    }
    func size(): Int64 {
        return items.size
    }
}

main() {
    let e = Add(Mul(Num(3), Num(4)), Neg(Num(5)))
    println("Expr: ${e.show()}")
    println("Eval: ${e.eval()}")
    println("Depth: ${depth(e)}")
    let exprs = ArrayList<Expr>()
    exprs.add(Num(7))
    exprs.add(Add(Num(1), Num(2)))
    exprs.add(Mul(Add(Num(2), Num(3)), Num(4)))
    exprs.add(Neg(Add(Num(10), Num(5))))
    println("=== Batch eval ===")
    var sum = 0
    for (ex in exprs) {
        let v = ex.eval()
        sum = sum + v
        println("${ex.show()} = ${v}")
    }
    println("Sum of all: ${sum}")
    let values = collectArrayList(exprs.iterator().map({ it => it.eval() }))
    println("Sorted values: ${String.join(collectArray<String>(({ => let _s = collectArrayList(values.iterator()); sort(_s, stable: true); _s })().iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("Max: ${values.iterator().reduce({a, b => if (a > b) { a } else { b }}) ?? 0}")
    println("=== Generic Stack ===")
    let st = Stack<Int64>()
    for (i in 1..=5) {
        st.push(i * i)
    }
    let drained = ArrayList<Int64>()
    while (!st.isEmpty()) {
        drained.add(st.pop())
    }
    println("Drained (LIFO): ${String.join(collectArray<String>(drained.iterator().map({e => e.toString()})), delimiter: " ")}")
    let names = Stack<String>()
    names.push("alpha")
    names.push("beta")
    names.push("gamma")
    println("Top: ${names.pop()}, remaining: ${names.size()}")
    println("=== Counting by depth ===")
    let depths = collectArrayList(exprs.iterator().map({ it => depth(it) }))
    var maxD = 0
    for (d in depths) {
        if (d > maxD) {
            maxD = d
        }
    }
    for (level in 1..=maxD) {
        var c = 0
        for (d in depths) {
            if (d == level) {
                c = c + 1
            }
        }
        println("depth ${level}: ${c} expr(s)")
    }
}
