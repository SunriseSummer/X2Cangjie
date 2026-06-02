import std.collection.*

open class Result {}

class Success <: Result {
    let value: Int64
    init(value: Int64) {
        this.value = value
    }
}

class Failure <: Result {
    let message: String
    init(message: String) {
        this.message = message
    }
}

class Pending <: Result {
    let progress: Int64
    init(progress: Int64) {
        this.progress = progress
    }
}

func describe(r: Result): String {
    return match (r) {
        case r: Success => "OK: ${r.value}"
        case r: Failure => "ERR: ${r.message}"
        case r: Pending => "WAIT: ${r.progress}%"
        case _ => throw Exception("")}
}

open class Token {}

class NumberToken <: Token {
    let value: Int64
    init(value: Int64) {
        this.value = value
    }
}

class PlusToken <: Token {}

class MinusToken <: Token {}

class MulToken <: Token {}

func tokenToString(t: Token): String {
    return match (t) {
        case t: NumberToken => t.value.toString()
        case t: PlusToken => "+"
        case t: MinusToken => "-"
        case t: MulToken => "*"
        case _ => throw Exception("")}
}

main() {
    let results = ArrayList<Result>([Success(42), Failure("not found"), Pending(75), Success(100), Failure("timeout")])
    for (r in results) {
        println(describe(r))
    }
    let tokens = ArrayList<Token>([NumberToken(3), PlusToken(), NumberToken(5), MulToken(), NumberToken(2)])
    let parts = ArrayList<String>()
    for (t in tokens) {
        parts.add(tokenToString(t))
    }
    println(String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " "))
    var successCount = 0
    var failCount = 0
    for (r in results) {
        match (r) {
            case r: Success => successCount += 1
            case r: Failure => failCount += 1
            case r: Pending => ()
            case _ => throw Exception("")}
    }
    println("Success: ${successCount}, Failures: ${failCount}")
}
