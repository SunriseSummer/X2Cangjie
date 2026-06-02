import std.collection.*
import std.deriving.*

@Derive[Equatable]
enum State <: ToString {
    | START | IN_WORD | IN_NUMBER | IN_STRING | DONE
    public func toString(): String {
    return match (this) {
                case START => "START"
            case IN_WORD => "IN_WORD"
            case IN_NUMBER => "IN_NUMBER"
            case IN_STRING => "IN_STRING"
            case DONE => "DONE"
}
    }
}

func lexAnalyze(input: String): ArrayList<String> {
    let tokens = ArrayList<String>()
    var state = State.START
    var buffer = StringBuilder()
    for (c in input.runes()) {
        match (state) {
            case State.START => 
                if ((c >= r'a' && c <= r'z') || (c >= r'A' && c <= r'Z')) {
                    state = State.IN_WORD
                    buffer.append(c)
                } else if (c >= r'0' && c <= r'9') {
                    state = State.IN_NUMBER
                    buffer.append(c)
                } else if (c == r'"') {
                    state = State.IN_STRING
                } else if (c == r' ') {} else {
                    tokens.add(c.toString())
                }
            case State.IN_WORD => 
                if (((c >= r'a' && c <= r'z') || (c >= r'A' && c <= r'Z')) || (c >= r'0' && c <= r'9')) {
                    buffer.append(c)
                } else {
                    tokens.add("WORD:${buffer}")
                    buffer = StringBuilder()
                    state = State.START
                    if (c != r' ') {
                        tokens.add(c.toString())
                    }
                }
            case State.IN_NUMBER => 
                if (c >= r'0' && c <= r'9') {
                    buffer.append(c)
                } else {
                    tokens.add("NUM:${buffer}")
                    buffer = StringBuilder()
                    state = State.START
                    if (c != r' ') {
                        tokens.add(c.toString())
                    }
                }
            case State.IN_STRING => 
                if (c == r'"') {
                    tokens.add("STR:${buffer}")
                    buffer = StringBuilder()
                    state = State.START
                } else {
                    buffer.append(c)
                }
            case State.DONE => ()}
    }
    let remaining = buffer.toString()
    if (!(remaining.isEmpty())) {
        match (state) {
            case State.IN_WORD => tokens.add("WORD:${remaining}")
            case State.IN_NUMBER => tokens.add("NUM:${remaining}")
            case _ => ()}
    }
    return tokens
}

main() {
    let tokens1 = lexAnalyze("hello 123 world")
    println(String.join(collectArray<String>(tokens1.iterator().map({e => e.toString()})), delimiter: ", "))
    let tokens2 = lexAnalyze("x+42*y")
    println(String.join(collectArray<String>(tokens2.iterator().map({e => e.toString()})), delimiter: ", "))
    let tokens3 = lexAnalyze("say \"hello world\" end")
    println(String.join(collectArray<String>(tokens3.iterator().map({e => e.toString()})), delimiter: ", "))
    let tokens4 = lexAnalyze("abc123 456def")
    println(String.join(collectArray<String>(tokens4.iterator().map({e => e.toString()})), delimiter: ", "))
}
