import std.collection.*
import std.deriving.*
import std.convert.*
import std.sort.*

@Derive[Equatable]
enum TokType <: ToString {
    | NUM | IDENT | OP | LPAREN | RPAREN | ASSIGN
    public func toString(): String {
    return match (this) {
                case NUM => "NUM"
            case IDENT => "IDENT"
            case OP => "OP"
            case LPAREN => "LPAREN"
            case RPAREN => "RPAREN"
            case ASSIGN => "ASSIGN"
}
    }
}

class Token <: ToString {
    let `type`: TokType
    let text: String
    init(`type`: TokType, text: String) {
        this.`type` = `type`
        this.text = text
    }
    public func toString(): String {
        return "Token(`type`=${this.`type`}, text=${this.text})"
    }
}

func isDigitCh(c: Rune): Bool {
    return c.isAsciiNumber()
}

func isAlphaCh(c: Rune): Bool {
    return c.isAsciiLetter()
}

func precedence(op: String): Int64 {
    return match (op) {
        case "+" => 1
        case "-" => 1
        case "*" => 2
        case "/" => 2
        case "%" => 2
        case "^" => 3
        case _ => 0}
}

func isRightAssoc(op: String): Bool {
    return op == "^"
}

class Tokenizer {
    let src: String
    init(src: String) {
        this.src = src
    }
    let tokens = ArrayList<Token>()
    func tokenize(): ArrayList<Token> {
        var i = 0
        let n = src.size
        while (i < n) {
            let c = src.toRuneArray()[i]
            if (c == r' ') {
                i = i + 1
            } else if (isDigitCh(c)) {
                let sb = StringBuilder()
                while ((i < n) && isDigitCh(src.toRuneArray()[i])) {
                    sb.append(src.toRuneArray()[i])
                    i = i + 1
                }
                tokens.add(Token(TokType.NUM, sb.toString()))
            } else if (isAlphaCh(c)) {
                let sb = StringBuilder()
                while ((i < n) && (isAlphaCh(src.toRuneArray()[i]) || isDigitCh(src.toRuneArray()[i]))) {
                    sb.append(src.toRuneArray()[i])
                    i = i + 1
                }
                tokens.add(Token(TokType.IDENT, sb.toString()))
            } else if (c == r'=') {
                tokens.add(Token(TokType.ASSIGN, "="))
                i = i + 1
            } else if (c == r'(') {
                tokens.add(Token(TokType.LPAREN, "("))
                i = i + 1
            } else if (c == r')') {
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
    func toRpn(tokens: ArrayList<Token>): ArrayList<Token> {
        let output = ArrayList<Token>()
        let opstack = ArrayList<Token>()
        for (t in tokens) {
            match (t.`type`) {
                case TokType.NUM => output.add(t)
                case TokType.IDENT => output.add(t)
                case TokType.OP => 
                    while (!(opstack.isEmpty())) {
                        let top = opstack[opstack.size - 1]
                        if (top.`type` != TokType.OP) {
                            break
                        }
                        let pt = precedence(top.text)
                        let ct = precedence(t.text)
                        if ((pt > ct) || ((pt == ct) && !isRightAssoc(t.text))) {
                            output.add(top)
                            opstack.remove(at: opstack.size - 1)
                        } else {
                            break
                        }
                    }
                    opstack.add(t)
                case TokType.LPAREN => opstack.add(t)
                case TokType.RPAREN => 
                    while (!(opstack.isEmpty()) && (opstack[opstack.size - 1].`type` != TokType.LPAREN)) {
                        output.add(opstack[opstack.size - 1])
                        opstack.remove(at: opstack.size - 1)
                    }
                    if (!(opstack.isEmpty())) {
                        opstack.remove(at: opstack.size - 1)
                    }
                case TokType.ASSIGN => opstack.add(t)}
        }
        while (!(opstack.isEmpty())) {
            output.add(opstack[opstack.size - 1])
            opstack.remove(at: opstack.size - 1)
        }
        return output
    }
}

func ipow(base: Int64, exp: Int64): Int64 {
    var result = 1
    var e = exp
    while (e > 0) {
        result = result * base
        e = e - 1
    }
    return result
}

func applyOp(op: String, a: Int64, b: Int64): Int64 {
    return match (op) {
        case "+" => a + b
        case "-" => a - b
        case "*" => a * b
        case "/" => a / b
        case "%" => a % b
        case "^" => ipow(a, b)
        case _ => 0}
}

class Evaluator {
    let vars = HashMap<String, Int64>()
    func valueOf(name: String): Int64 {
        return vars.get(name) ?? 0
    }
    func evalRpn(rpn: ArrayList<Token>): Int64 {
        let stack = ArrayList<Int64>()
        for (t in rpn) {
            match (t.`type`) {
                case TokType.NUM => stack.add(Int64.parse(t.text))
                case TokType.IDENT => stack.add(valueOf(t.text))
                case TokType.OP => 
                    if (stack.size >= 2) {
                        let b = stack[stack.size - 1]
                        let a = stack[stack.size - 2]
                        stack.remove(at: stack.size - 1)
                        stack.remove(at: stack.size - 1)
                        stack.add(applyOp(t.text, a, b))
                    }
                case _ => ()}
        }
        if (stack.isEmpty()) {
            return 0
        }
        return stack[stack.size - 1]
    }
    func run(line: String): Int64 {
        let eqIdx = (line.indexOf("=") ?? -1)
        if (eqIdx >= 0) {
            let name = line[0..eqIdx].trimAscii()
            let expr = line[eqIdx + 1..].trimAscii()
            let toks = Tokenizer(expr).tokenize()
            let rpn = ShuntingYard().toRpn(toks)
            let v = evalRpn(rpn)
            vars[name] = v
            return v
        } else {
            let toks = Tokenizer(line).tokenize()
            let rpn = ShuntingYard().toRpn(toks)
            return evalRpn(rpn)
        }
    }
}

func rpnString(rpn: ArrayList<Token>): String {
    return String.join(collectArray<String>(collectArrayList(rpn.iterator().map({ it => it.text })).iterator().map({e => e.toString()})), delimiter: " ")
}

func toBinary(n: Int64): String {
    if (n == 0) {
        return "0"
    }
    var x = n
    let sb = StringBuilder()
    while (x > 0) {
        let bit = x % 2
        sb.append(Rune(UInt32(Int64(UInt32(r'0')) + bit)))
        x = x / 2
    }
    return ({ => let _r = sb.toString().toRuneArray(); String(Array<Rune>(_r.size, {j => _r[_r.size - 1 - j]})) })()
}

func toHex(n: Int64): String {
    if (n == 0) {
        return "0"
    }
    let digits = "0123456789abcdef"
    var x = n
    let sb = StringBuilder()
    while (x > 0) {
        let d = x % 16
        sb.append(digits.toRuneArray()[d])
        x = x / 16
    }
    return ({ => let _r = sb.toString().toRuneArray(); String(Array<Rune>(_r.size, {j => _r[_r.size - 1 - j]})) })()
}

func romanDigit(value: Int64, one: String, five: String, ten: String): String {
    return if (value >= 1 && value <= 3) {
        (one * value)
    } else if (value == 4) {
        one + five
    } else if (value >= 5 && value <= 8) {
        five + (one * (value - 5))
    } else if (value == 9) {
        one + ten
    } else {
        ""
    }
}

func toRoman(n: Int64): String {
    var x = n
    let sb = StringBuilder()
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

class Series {
    let name: String
    init(name: String) {
        this.name = name
    }
    let data = ArrayList<Int64>()
    func push(x: Int64) {
        data.add(x)
    }
    func total(): Int64 {
        return data.iterator().fold<Int64>(0, {acc, x => acc + x})
    }
    func mean(): Int64 {
        if (data.isEmpty()) {
            return 0
        }
        return data.iterator().fold<Int64>(0, {acc, x => acc + x}) / data.size
    }
    func variance(): Int64 {
        if (data.isEmpty()) {
            return 0
        }
        let m = mean()
        var acc = 0
        for (v in data) {
            acc = acc + ((v - m) * (v - m))
        }
        return acc / data.size
    }
    func range(): Int64 {
        let mx = data.iterator().reduce({a, b => if (a > b) { a } else { b }}) ?? 0
        let mn = data.iterator().reduce({a, b => if (a < b) { a } else { b }}) ?? 0
        return mx - mn
    }
}

func applyUnary(fn: String, x: Int64): Int64 {
    return match (fn) {
        case "neg" => -x
        case "sqr" => x * x
        case "dbl" => x * 2
        case "abs" => 
            if (x < 0) {
                -x
            } else {
                x
            }
        case "inc" => x + 1
        case _ => x}
}

main() {
    println("=== Tokenizer ===")
    let sample = "3 + 4 * 2 - 1"
    let toks = Tokenizer(sample).tokenize()
    println("Tokens: ${toks.size}")
    for (t in toks) {
        println("${t.`type`} '${t.text}'")
    }
    println("=== RPN ===")
    let rpn = ShuntingYard().toRpn(toks)
    println(rpnString(rpn))
    println("=== Eval ===")
    let ev = Evaluator()
    let exprs = ArrayList(["1 + 2 + 3", "2 * 3 + 4", "2 + 3 * 4", "( 1 + 2 ) * 3", "2 ^ 3 ^ 2", "10 - 2 - 3", "100 / 5 / 2", "7 % 3 + 1"])
    for (e in exprs) {
        let r = ev.run(e)
        println("${e} = ${r}")
    }
    println("=== Script ===")
    let script = ArrayList(["x = 5", "y = x * 2", "z = x + y", "w = z ^ 2 - x", "x + y + z + w"])
    for (line in script) {
        let r = ev.run(line)
        println("${line}  -> ${r}")
    }
    println("=== Variables ===")
    let names = ArrayList<String>()
    for (k in ev.vars.keys()) {
        names.add(k)
    }
    let sortedNames = ({ => let _s = collectArrayList(names.iterator()); sort(_s, stable: true); _s })()
    for (k in sortedNames) {
        println("${k} = ${ev.valueOf(k)}")
    }
    println("=== Stats ===")
    let values = ArrayList<Int64>()
    for (k in sortedNames) {
        values.add(ev.valueOf(k))
    }
    println("Count: ${values.size}")
    println("Sum: ${values.iterator().fold<Int64>(0, {acc, x => acc + x})}")
    println("Max: ${values.iterator().reduce({a, b => if (a > b) { a } else { b }}) ?? 0}")
    println("Min: ${values.iterator().reduce({a, b => if (a < b) { a } else { b }}) ?? 0}")
    let evens = collectArrayList(values.iterator().filter({ it => (it % 2) == 0 }))
    println("Evens: ${evens.size}")
    println("=== Batch Eval ===")
    var grand = 0
    for (i in 1..=5) {
        let expr = "${i} * ${i} + ${i}"
        let r = ev.run(expr)
        grand = grand + r
        println("${expr} = ${r}")
    }
    println("Grand total: ${grand}")
    println("=== Precedence Table ===")
    let ops = ArrayList(["+", "-", "*", "/", "%", "^"])
    for (op in ops) {
        println("${op} -> ${precedence(op)} rightAssoc=${isRightAssoc(op)}")
    }
    println("=== Histogram of Results ===")
    let results = HashMap<Int64, Int64>()
    for (i in 1..=10) {
        let r = ev.run("${i} % 3")
        results[r] = (results.get(r) ?? 0) + 1
    }
    for (bucket in 0..=2) {
        let c = results.get(bucket) ?? 0
        println("${bucket}: ${("*" * c)}")
    }
    println("=== Number Formats ===")
    for (n in ArrayList([0, 5, 10, 42, 255, 1000])) {
        println("${n} -> bin=${toBinary(n)} hex=${toHex(n)} roman=${toRoman(n)}")
    }
    println("=== Series Stats ===")
    let s = Series("temps")
    for (v in ArrayList([20, 22, 19, 25, 23, 21, 18, 24])) {
        s.push(v)
    }
    println("name=${s.name} n=${s.data.size}")
    println("total=${s.total()} mean=${s.mean()} variance=${s.variance()} range=${s.range()}")
    println("=== Unary Functions ===")
    let fns = ArrayList(["neg", "sqr", "dbl", "abs", "inc"])
    for (fn in fns) {
        let outs = ArrayList<Int64>()
        for (x in ArrayList([-2, 0, 3, 5])) {
            outs.add(applyUnary(fn, x))
        }
        println("${fn}: ${String.join(collectArray<String>(outs.iterator().map({e => e.toString()})), delimiter: ", ")}")
    }
    println("=== Multiplication Table ===")
    for (i in 1..=5) {
        let row = ArrayList<String>()
        for (j in 1..=5) {
            row.add((i * j).toString())
        }
        println(String.join(collectArray<String>(row.iterator().map({e => e.toString()})), delimiter: " "))
    }
    println("=== Expression Matrix ===")
    let ev2 = Evaluator()
    ev2.run("a = 4")
    ev2.run("b = 7")
    let forms = ArrayList(["a + b", "a * b", "b - a", "a ^ 2 + b"])
    for (f in forms) {
        println("${f} = ${ev2.run(f)}")
    }
    println("=== Word Frequencies ===")
    let text = "the cat sat on the mat the cat ran"
    let freq = HashMap<String, Int64>()
    for (w in text.split(" ")) {
        freq[w] = (freq.get(w) ?? 0) + 1
    }
    let keys = ArrayList<String>()
    for (k in freq.keys()) {
        keys.add(k)
    }
    for (k in ({ => let _s = collectArrayList(keys.iterator()); sort(_s, stable: true); _s })()) {
        println("${k}: ${freq.get(k) ?? 0}")
    }
    println("=== Digit Sums ===")
    for (n in ArrayList([123, 4567, 89, 100000])) {
        var x = n
        var sum = 0
        while (x > 0) {
            sum = sum + (x % 10)
            x = x / 10
        }
        println("${n} -> ${sum}")
    }
    println("=== Prime Sieve ===")
    let limit = 30
    let isComposite = Array(limit + 1, { _idx => false })
    let primes = ArrayList<Int64>()
    for (p in 2..=limit) {
        if (!isComposite[p]) {
            primes.add(p)
            var m = p * p
            while (m <= limit) {
                isComposite[m] = true
                m = m + p
            }
        }
    }
    println("Primes up to ${limit}: ${String.join(collectArray<String>(primes.iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("Count: ${primes.size}, Sum: ${primes.iterator().fold<Int64>(0, {acc, x => acc + x})}")
    println("=== Fibonacci ===")
    let memo = HashMap<Int64, Int64>()
    memo[0] = 0
    memo[1] = 1
    for (i in 2..=15) {
        memo[i] = (memo.get(i - 1) ?? 0) + (memo.get(i - 2) ?? 0)
    }
    let fibs = ArrayList<Int64>()
    for (i in 0..=15) {
        fibs.add(memo.get(i) ?? 0)
    }
    println(String.join(collectArray<String>(fibs.iterator().map({e => e.toString()})), delimiter: " "))
    println("=== Matrix Transpose ===")
    let matrix = ArrayList([ArrayList([1, 2, 3]), ArrayList([4, 5, 6])])
    let rows = matrix.size
    let cols = matrix[0].size
    for (c in 0..cols) {
        let line = ArrayList<Int64>()
        for (r in 0..rows) {
            line.add(matrix[r][c])
        }
        println(String.join(collectArray<String>(line.iterator().map({e => e.toString()})), delimiter: " "))
    }
    println("=== Running Totals ===")
    let seq = ArrayList([3, 1, 4, 1, 5, 9, 2, 6])
    var acc = 0
    let totals = ArrayList<Int64>()
    for (v in seq) {
        acc = acc + v
        totals.add(acc)
    }
    println(String.join(collectArray<String>(totals.iterator().map({e => e.toString()})), delimiter: ", "))
    println("=== Bracket Check ===")
    let samples = ArrayList(["(())", "(()", "()()", ")(", "((()))"])
    for (sample in samples) {
        var depth = 0
        var ok = true
        for (ch in sample.runes()) {
            if (ch == r'(') {
                depth = depth + 1
            } else if (ch == r')') {
                depth = depth - 1
            }
            if (depth < 0) {
                ok = false
            }
        }
        if (depth != 0) {
            ok = false
        }
        println("${sample} -> ${ok}")
    }
}
