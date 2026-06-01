// ~500-line real-world style program: a tiny calculator language.
// Tokenizer + shunting-yard to RPN + RPN evaluator with variables,
// plus a small REPL-style script runner and reporting.

enum class TokType { NUM, IDENT, OP, LPAREN, RPAREN, ASSIGN }

data class Token(val type: TokType, val text: String)

fun isDigitCh(c: Char): Boolean {
    return c.isDigit()
}

fun isAlphaCh(c: Char): Boolean {
    return c.isLetter()
}

fun precedence(op: String): Int {
    return when (op) {
        "+" -> 1
        "-" -> 1
        "*" -> 2
        "/" -> 2
        "%" -> 2
        "^" -> 3
        else -> 0
    }
}

fun isRightAssoc(op: String): Boolean {
    return op == "^"
}

class Tokenizer(val src: String) {
    val tokens = ArrayList<Token>()

    fun tokenize(): List<Token> {
        var i = 0
        val n = src.length
        while (i < n) {
            val c = src[i]
            if (c == ' ') {
                i = i + 1
            } else if (isDigitCh(c)) {
                val sb = StringBuilder()
                while (i < n && isDigitCh(src[i])) {
                    sb.append(src[i])
                    i = i + 1
                }
                tokens.add(Token(TokType.NUM, sb.toString()))
            } else if (isAlphaCh(c)) {
                val sb = StringBuilder()
                while (i < n && (isAlphaCh(src[i]) || isDigitCh(src[i]))) {
                    sb.append(src[i])
                    i = i + 1
                }
                tokens.add(Token(TokType.IDENT, sb.toString()))
            } else if (c == '=') {
                tokens.add(Token(TokType.ASSIGN, "="))
                i = i + 1
            } else if (c == '(') {
                tokens.add(Token(TokType.LPAREN, "("))
                i = i + 1
            } else if (c == ')') {
                tokens.add(Token(TokType.RPAREN, ")"))
                i = i + 1
            } else {
                tokens.add(Token(TokType.OP, c.toString()))
                i = i + 1
            }
        }
        return tokens
    }
}

class ShuntingYard {
    fun toRpn(tokens: List<Token>): List<Token> {
        val output = ArrayList<Token>()
        val opstack = ArrayList<Token>()
        for (t in tokens) {
            when (t.type) {
                TokType.NUM -> output.add(t)
                TokType.IDENT -> output.add(t)
                TokType.OP -> {
                    while (opstack.isNotEmpty()) {
                        val top = opstack[opstack.size - 1]
                        if (top.type != TokType.OP) {
                            break
                        }
                        val pt = precedence(top.text)
                        val ct = precedence(t.text)
                        if (pt > ct || (pt == ct && !isRightAssoc(t.text))) {
                            output.add(top)
                            opstack.removeAt(opstack.size - 1)
                        } else {
                            break
                        }
                    }
                    opstack.add(t)
                }
                TokType.LPAREN -> opstack.add(t)
                TokType.RPAREN -> {
                    while (opstack.isNotEmpty() && opstack[opstack.size - 1].type != TokType.LPAREN) {
                        output.add(opstack[opstack.size - 1])
                        opstack.removeAt(opstack.size - 1)
                    }
                    if (opstack.isNotEmpty()) {
                        opstack.removeAt(opstack.size - 1)
                    }
                }
                TokType.ASSIGN -> opstack.add(t)
            }
        }
        while (opstack.isNotEmpty()) {
            output.add(opstack[opstack.size - 1])
            opstack.removeAt(opstack.size - 1)
        }
        return output
    }
}

fun ipow(base: Int, exp: Int): Int {
    var result = 1
    var e = exp
    while (e > 0) {
        result = result * base
        e = e - 1
    }
    return result
}

fun applyOp(op: String, a: Int, b: Int): Int {
    return when (op) {
        "+" -> a + b
        "-" -> a - b
        "*" -> a * b
        "/" -> a / b
        "%" -> a % b
        "^" -> ipow(a, b)
        else -> 0
    }
}

class Evaluator {
    val vars = HashMap<String, Int>()

    fun valueOf(name: String): Int {
        return vars[name] ?: 0
    }

    fun evalRpn(rpn: List<Token>): Int {
        val stack = ArrayList<Int>()
        for (t in rpn) {
            when (t.type) {
                TokType.NUM -> stack.add(t.text.toInt())
                TokType.IDENT -> stack.add(valueOf(t.text))
                TokType.OP -> {
                    if (stack.size >= 2) {
                        val b = stack[stack.size - 1]
                        val a = stack[stack.size - 2]
                        stack.removeAt(stack.size - 1)
                        stack.removeAt(stack.size - 1)
                        stack.add(applyOp(t.text, a, b))
                    }
                }
                else -> {
                }
            }
        }
        if (stack.isEmpty()) {
            return 0
        }
        return stack[stack.size - 1]
    }

    fun run(line: String): Int {
        val eqIdx = line.indexOf('=')
        if (eqIdx >= 0) {
            val name = line.substring(0, eqIdx).trim()
            val expr = line.substring(eqIdx + 1).trim()
            val toks = Tokenizer(expr).tokenize()
            val rpn = ShuntingYard().toRpn(toks)
            val v = evalRpn(rpn)
            vars[name] = v
            return v
        } else {
            val toks = Tokenizer(line).tokenize()
            val rpn = ShuntingYard().toRpn(toks)
            return evalRpn(rpn)
        }
    }
}

fun rpnString(rpn: List<Token>): String {
    return rpn.map { it.text }.joinToString(" ")
}

// ---- number formatting helpers (char-level) ----

fun toBinary(n: Int): String {
    if (n == 0) {
        return "0"
    }
    var x = n
    val sb = StringBuilder()
    while (x > 0) {
        val bit = x % 2
        sb.append(('0' + bit))
        x = x / 2
    }
    return sb.toString().reversed()
}

fun toHex(n: Int): String {
    if (n == 0) {
        return "0"
    }
    val digits = "0123456789abcdef"
    var x = n
    val sb = StringBuilder()
    while (x > 0) {
        val d = x % 16
        sb.append(digits[d])
        x = x / 16
    }
    return sb.toString().reversed()
}

fun romanDigit(value: Int, one: String, five: String, ten: String): String {
    return when (value) {
        in 1..3 -> one.repeat(value)
        4 -> one + five
        in 5..8 -> five + one.repeat(value - 5)
        9 -> one + ten
        else -> ""
    }
}

fun toRoman(n: Int): String {
    var x = n
    val sb = StringBuilder()
    while (x >= 1000) {
        sb.append("M")
        x = x - 1000
    }
    sb.append(romanDigit(x / 100, "C", "D", "M"))
    x = x % 100
    sb.append(romanDigit(x / 10, "X", "L", "C"))
    x = x % 10
    sb.append(romanDigit(x, "I", "V", "X"))
    return sb.toString()
}

// ---- simple statistics over a series ----

class Series(val name: String) {
    val data = ArrayList<Int>()
    fun push(x: Int) {
        data.add(x)
    }
    fun total(): Int {
        return data.sum()
    }
    fun mean(): Int {
        if (data.isEmpty()) {
            return 0
        }
        return data.sum() / data.size
    }
    fun variance(): Int {
        if (data.isEmpty()) {
            return 0
        }
        val m = mean()
        var acc = 0
        for (v in data) {
            acc = acc + (v - m) * (v - m)
        }
        return acc / data.size
    }
    fun range(): Int {
        val mx = data.maxOrNull() ?: 0
        val mn = data.minOrNull() ?: 0
        return mx - mn
    }
}

// ---- function registry for the calculator ----

fun applyUnary(fn: String, x: Int): Int {
    return when (fn) {
        "neg" -> -x
        "sqr" -> x * x
        "dbl" -> x * 2
        "abs" -> if (x < 0) -x else x
        "inc" -> x + 1
        else -> x
    }
}

fun main() {
    println("=== Tokenizer ===")
    val sample = "3 + 4 * 2 - 1"
    val toks = Tokenizer(sample).tokenize()
    println("Tokens: ${toks.size}")
    for (t in toks) {
        println("${t.type} '${t.text}'")
    }

    println("=== RPN ===")
    val rpn = ShuntingYard().toRpn(toks)
    println(rpnString(rpn))

    println("=== Eval ===")
    val ev = Evaluator()
    val exprs = listOf(
        "1 + 2 + 3",
        "2 * 3 + 4",
        "2 + 3 * 4",
        "( 1 + 2 ) * 3",
        "2 ^ 3 ^ 2",
        "10 - 2 - 3",
        "100 / 5 / 2",
        "7 % 3 + 1"
    )
    for (e in exprs) {
        val r = ev.run(e)
        println("$e = $r")
    }

    println("=== Script ===")
    val script = listOf(
        "x = 5",
        "y = x * 2",
        "z = x + y",
        "w = z ^ 2 - x",
        "x + y + z + w"
    )
    for (line in script) {
        val r = ev.run(line)
        println("$line  -> $r")
    }

    println("=== Variables ===")
    val names = ArrayList<String>()
    for (k in ev.vars.keys) {
        names.add(k)
    }
    val sortedNames = names.sorted()
    for (k in sortedNames) {
        println("$k = ${ev.valueOf(k)}")
    }

    println("=== Stats ===")
    val values = ArrayList<Int>()
    for (k in sortedNames) {
        values.add(ev.valueOf(k))
    }
    println("Count: ${values.size}")
    println("Sum: ${values.sum()}")
    println("Max: ${values.maxOrNull() ?: 0}")
    println("Min: ${values.minOrNull() ?: 0}")
    val evens = values.filter { it % 2 == 0 }
    println("Evens: ${evens.size}")

    println("=== Batch Eval ===")
    var grand = 0
    for (i in 1..5) {
        val expr = "$i * $i + $i"
        val r = ev.run(expr)
        grand = grand + r
        println("$expr = $r")
    }
    println("Grand total: $grand")

    println("=== Precedence Table ===")
    val ops = listOf("+", "-", "*", "/", "%", "^")
    for (op in ops) {
        println("$op -> ${precedence(op)} rightAssoc=${isRightAssoc(op)}")
    }

    println("=== Histogram of Results ===")
    val results = HashMap<Int, Int>()
    for (i in 1..10) {
        val r = ev.run("$i % 3")
        results[r] = (results[r] ?: 0) + 1
    }
    for (bucket in 0..2) {
        val c = results[bucket] ?: 0
        println("$bucket: ${"*".repeat(c)}")
    }

    println("=== Number Formats ===")
    for (n in listOf(0, 5, 10, 42, 255, 1000)) {
        println("$n -> bin=${toBinary(n)} hex=${toHex(n)} roman=${toRoman(n)}")
    }

    println("=== Series Stats ===")
    val s = Series("temps")
    for (v in listOf(20, 22, 19, 25, 23, 21, 18, 24)) {
        s.push(v)
    }
    println("name=${s.name} n=${s.data.size}")
    println("total=${s.total()} mean=${s.mean()} variance=${s.variance()} range=${s.range()}")

    println("=== Unary Functions ===")
    val fns = listOf("neg", "sqr", "dbl", "abs", "inc")
    for (fn in fns) {
        val outs = ArrayList<Int>()
        for (x in listOf(-2, 0, 3, 5)) {
            outs.add(applyUnary(fn, x))
        }
        println("$fn: ${outs.joinToString(", ")}")
    }

    println("=== Multiplication Table ===")
    for (i in 1..5) {
        val row = ArrayList<String>()
        for (j in 1..5) {
            row.add((i * j).toString())
        }
        println(row.joinToString(" "))
    }

    println("=== Expression Matrix ===")
    val ev2 = Evaluator()
    ev2.run("a = 4")
    ev2.run("b = 7")
    val forms = listOf("a + b", "a * b", "b - a", "a ^ 2 + b")
    for (f in forms) {
        println("$f = ${ev2.run(f)}")
    }

    println("=== Word Frequencies ===")
    val text = "the cat sat on the mat the cat ran"
    val freq = HashMap<String, Int>()
    for (w in text.split(" ")) {
        freq[w] = (freq[w] ?: 0) + 1
    }
    val keys = ArrayList<String>()
    for (k in freq.keys) {
        keys.add(k)
    }
    for (k in keys.sorted()) {
        println("$k: ${freq[k] ?: 0}")
    }

    println("=== Digit Sums ===")
    for (n in listOf(123, 4567, 89, 100000)) {
        var x = n
        var sum = 0
        while (x > 0) {
            sum = sum + x % 10
            x = x / 10
        }
        println("$n -> $sum")
    }

    println("=== Prime Sieve ===")
    val limit = 30
    val isComposite = Array(limit + 1) { false }
    val primes = ArrayList<Int>()
    for (p in 2..limit) {
        if (!isComposite[p]) {
            primes.add(p)
            var m = p * p
            while (m <= limit) {
                isComposite[m] = true
                m = m + p
            }
        }
    }
    println("Primes up to $limit: ${primes.joinToString(", ")}")
    println("Count: ${primes.size}, Sum: ${primes.sum()}")

    println("=== Fibonacci ===")
    val memo = HashMap<Int, Int>()
    memo[0] = 0
    memo[1] = 1
    for (i in 2..15) {
        memo[i] = (memo[i - 1] ?: 0) + (memo[i - 2] ?: 0)
    }
    val fibs = ArrayList<Int>()
    for (i in 0..15) {
        fibs.add(memo[i] ?: 0)
    }
    println(fibs.joinToString(" "))

    println("=== Matrix Transpose ===")
    val matrix = listOf(
        listOf(1, 2, 3),
        listOf(4, 5, 6)
    )
    val rows = matrix.size
    val cols = matrix[0].size
    for (c in 0 until cols) {
        val line = ArrayList<Int>()
        for (r in 0 until rows) {
            line.add(matrix[r][c])
        }
        println(line.joinToString(" "))
    }

    println("=== Running Totals ===")
    val seq = listOf(3, 1, 4, 1, 5, 9, 2, 6)
    var acc = 0
    val totals = ArrayList<Int>()
    for (v in seq) {
        acc = acc + v
        totals.add(acc)
    }
    println(totals.joinToString(", "))

    println("=== Bracket Check ===")
    val samples = listOf("(())", "(()", "()()", ")(", "((()))")
    for (sample in samples) {
        var depth = 0
        var ok = true
        for (ch in sample) {
            if (ch == '(') {
                depth = depth + 1
            } else if (ch == ')') {
                depth = depth - 1
            }
            if (depth < 0) {
                ok = false
            }
        }
        if (depth != 0) {
            ok = false
        }
        println("$sample -> $ok")
    }
}
