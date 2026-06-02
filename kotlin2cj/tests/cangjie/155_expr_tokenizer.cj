import std.collection.*

func tokenize(expr: String): ArrayList<String> {
    let tokens = ArrayList<String>()
    var i = 0
    while (i < expr.size) {
        let c = expr.toRuneArray()[i]
        if (c == r' ') {
            i += 1
            continue
        }
        if ((((((c == r'+') || (c == r'-')) || (c == r'*')) || (c == r'/')) || (c == r'(')) || (c == r')')) {
            tokens.add(c.toString())
            i += 1
        } else if (c >= r'0' && c <= r'9') {
            let sb = StringBuilder()
            while ((i < expr.size) && (expr.toRuneArray()[i] >= r'0' && expr.toRuneArray()[i] <= r'9')) {
                sb.append(expr.toRuneArray()[i])
                i += 1
            }
            tokens.add(sb.toString())
        } else {
            i += 1
        }
    }
    return tokens
}

func evalSimple(tokens: ArrayList<String>): Int64 {
    if (tokens.isEmpty()) {
        return 0
    }
    var result = 0
    var sign = 1
    for (token in tokens) {
        if (token == "+") {
            sign = 1
        } else if (token == "-") {
            sign = -1
        } else if ((((token != "(") && (token != ")")) && (token != "*")) && (token != "/")) {
            var num = 0
            for (c in token.runes()) {
                num = (num * 10) + ((Int64(UInt32(c)) - Int64(UInt32(r'0'))))
            }
            result += sign * num
        }
    }
    return result
}

func isBalancedParens(s: String): Bool {
    var count = 0
    for (c in s.runes()) {
        if (c == r'(') {
            count += 1
        }
        if (c == r')') {
            count -= 1
        }
        if (count < 0) {
            return false
        }
    }
    return count == 0
}

main() {
    let t1 = tokenize("12 + 34 - 5")
    println(String.join(collectArray<String>(t1.iterator().map({e => e.toString()})), delimiter: ", "))
    let t2 = tokenize("(1+2)*3")
    println(String.join(collectArray<String>(t2.iterator().map({e => e.toString()})), delimiter: ", "))
    println("12+34-5 = ${evalSimple(tokenize("12 + 34 - 5"))}")
    println("100-30-20 = ${evalSimple(tokenize("100 - 30 - 20"))}")
    println("1+2+3+4+5 = ${evalSimple(tokenize("1+2+3+4+5"))}")
    println(isBalancedParens("()"))
    println(isBalancedParens("(())"))
    println(isBalancedParens("(()(()))"))
    println(isBalancedParens(")("))
    println(isBalancedParens("(()"))
}
