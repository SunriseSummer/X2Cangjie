import std.collection.*
import std.deriving.*

@Derive[Equatable]
enum Op <: ToString {
    | ADD | SUB | MUL
    public func toString(): String {
    return match (this) {
                case ADD => "ADD"
            case SUB => "SUB"
            case MUL => "MUL"
}
    }
}

func apply(op: Op, a: Int64, b: Int64): Int64 {
    return match (op) {
        case Op.ADD => a + b
        case Op.SUB => a - b
        case Op.MUL => a * b}
}

main() {
    let ops = ArrayList([Op.ADD, Op.SUB, Op.MUL])
    for (op in ops) {
        println("${op}: ${apply(op, 6, 4)}")
    }
    let results = collectArrayList(ops.iterator().map({ it => apply(it, 10, 3) }))
    println("sum=${results.iterator().fold<Int64>(0, {acc, x => acc + x})}")
}
