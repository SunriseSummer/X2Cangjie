import std.collection.*
import std.convert.*

func evalRpn(expr: String): Int64 {
    let stack = ArrayList<Int64>()
    let tokens = collectArrayList(expr.split(" ").iterator())
    for (tok in tokens) {
        if (ArrayList(["+", "-", "*", "/"]).contains(tok)) {
            let b = stack.remove(at: stack.size - 1)
            let a = stack.remove(at: stack.size - 1)
            let r = match (tok) {
                case "+" => a + b
                case "-" => a - b
                case "*" => a * b
                case _ => a / b}
            stack.add(r)
        } else {
            stack.add(Int64.parse(tok))
        }
    }
    return stack[stack.size - 1]
}

main() {
    println(evalRpn("3 4 +"))
    println(evalRpn("5 1 2 + 4 * + 3 -"))
    println(evalRpn("2 3 4 * +"))
}
