// Complex string parsing: simple expression tokenizer and evaluator
fun tokenize(expr: String): ArrayList<String> {
    val tokens = ArrayList<String>()
    var i = 0
    while (i < expr.length) {
        val c = expr[i]
        if (c == ' ') {
            i++
            continue
        }
        if (c == '+' || c == '-' || c == '*' || c == '/' || c == '(' || c == ')') {
            tokens.add(c.toString())
            i++
        } else if (c in '0'..'9') {
            val sb = StringBuilder()
            while (i < expr.length && expr[i] in '0'..'9') {
                sb.append(expr[i])
                i++
            }
            tokens.add(sb.toString())
        } else {
            i++
        }
    }
    return tokens
}

// Simple evaluator for +/- only (no precedence needed for this subset)
fun evalSimple(tokens: ArrayList<String>): Int {
    if (tokens.isEmpty()) return 0
    var result = 0
    var sign = 1
    for (token in tokens) {
        if (token == "+") {
            sign = 1
        } else if (token == "-") {
            sign = -1
        } else if (token != "(" && token != ")" && token != "*" && token != "/") {
            // It's a number
            var num = 0
            for (c in token) {
                num = num * 10 + (c - '0')
            }
            result += sign * num
        }
    }
    return result
}

fun isBalancedParens(s: String): Boolean {
    var count = 0
    for (c in s) {
        if (c == '(') count++
        if (c == ')') count--
        if (count < 0) return false
    }
    return count == 0
}

fun main() {
    // Tokenize
    val t1 = tokenize("12 + 34 - 5")
    println(t1.joinToString(", "))

    val t2 = tokenize("(1+2)*3")
    println(t2.joinToString(", "))

    // Eval simple
    println("12+34-5 = ${evalSimple(tokenize("12 + 34 - 5"))}")
    println("100-30-20 = ${evalSimple(tokenize("100 - 30 - 20"))}")
    println("1+2+3+4+5 = ${evalSimple(tokenize("1+2+3+4+5"))}")

    // Balanced parens
    println(isBalancedParens("()"))
    println(isBalancedParens("(())"))
    println(isBalancedParens("(()(()))"))
    println(isBalancedParens(")("))
    println(isBalancedParens("(()"))
}
