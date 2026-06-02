import std.collection.*
import std.deriving.*
import std.convert.*
import std.sort.*

func gcd(a: Int64, b: Int64): Int64 {
    var x = a
    var y = b
    while (y != 0) {
        let t = y
        y = x % y
        x = t
    }
    return x
}

func lcm(a: Int64, b: Int64): Int64 {
    return (a / gcd(a, b)) * b
}

func isPrime(n: Int64): Bool {
    if (n < 2) {
        return false
    }
    var i = 2
    while ((i * i) <= n) {
        if ((n % i) == 0) {
            return false
        }
        i += 1
    }
    return true
}

func primesUpTo(n: Int64): ArrayList<Int64> {
    let result = ArrayList<Int64>()
    var i = 2
    while (i <= n) {
        if (isPrime(i)) {
            result.add(i)
        }
        i += 1
    }
    return result
}

func factorial(n: Int64): Int64 {
    var r = 1
    var i = 2
    while (i <= n) {
        r *= i
        i += 1
    }
    return r
}

func fib(n: Int64): Int64 {
    if (n < 2) {
        return Int64(n)
    }
    var a = 0
    var b = 1
    var i = 2
    while (i <= n) {
        let c = a + b
        a = b
        b = c
        i += 1
    }
    return b
}

func power(base: Int64, exp: Int64): Int64 {
    var r = 1
    var i = 0
    while (i < exp) {
        r *= base
        i += 1
    }
    return r
}

func digitSum(n: Int64): Int64 {
    var x = if (n < 0) {
        -n
    } else {
        n
    }
    var s = 0
    while (x > 0) {
        s += x % 10
        x /= 10
    }
    return s
}

func reverseInt(n: Int64): Int64 {
    var x = if (n < 0) {
        -n
    } else {
        n
    }
    var r = 0
    while (x > 0) {
        r = (r * 10) + (x % 10)
        x /= 10
    }
    return if (n < 0) {
        -r
    } else {
        r
    }
}

func isPalindromeInt(n: Int64): Bool {
    return n == reverseInt(n)
}

func clampInt(v: Int64, lo: Int64, hi: Int64): Int64 {
    if (v < lo) {
        return lo
    }
    if (v > hi) {
        return hi
    }
    return v
}

func maxOfThree(a: Int64, b: Int64, c: Int64): Int64 {
    var m = a
    if (b > m) {
        m = b
    }
    if (c > m) {
        m = c
    }
    return m
}

func minOfThree(a: Int64, b: Int64, c: Int64): Int64 {
    var m = a
    if (b < m) {
        m = b
    }
    if (c < m) {
        m = c
    }
    return m
}

func sumRange(lo: Int64, hi: Int64): Int64 {
    var s = 0
    var i = lo
    while (i <= hi) {
        s += i
        i += 1
    }
    return s
}

func countDivisors(n: Int64): Int64 {
    var cnt = 0
    var i = 1
    while (i <= n) {
        if ((n % i) == 0) {
            cnt += 1
        }
        i += 1
    }
    return cnt
}

func isPerfect(n: Int64): Bool {
    var s = 0
    var i = 1
    while (i < n) {
        if ((n % i) == 0) {
            s += i
        }
        i += 1
    }
    return s == n
}

func reverseString(s: String): String {
    let sb = StringBuilder()
    var i = s.size - 1
    while (i >= 0) {
        sb.append(s.toRuneArray()[i])
        i -= 1
    }
    return sb.toString()
}

func isPalindrome(s: String): Bool {
    var i = 0
    var j = s.size - 1
    while (i < j) {
        if (s.toRuneArray()[i] != s.toRuneArray()[j]) {
            return false
        }
        i += 1
        j -= 1
    }
    return true
}

func countVowels(s: String): Int64 {
    var c = 0
    for (ch in s.runes()) {
        if (((((ch == r'a') || (ch == r'e')) || (ch == r'i')) || (ch == r'o')) || (ch == r'u')) {
            c += 1
        }
    }
    return c
}

func countChar(s: String, target: Rune): Int64 {
    var c = 0
    for (ch in s.runes()) {
        if (ch == target) {
            c += 1
        }
    }
    return c
}

func toUpperFirst(s: String): String {
    if (s.isEmpty()) {
        return s
    }
    return s[0..1].toAsciiUpper() + s[1..]
}

func repeatString(s: String, n: Int64): String {
    let sb = StringBuilder()
    var i = 0
    while (i < n) {
        sb.append(s)
        i += 1
    }
    return sb.toString()
}

func countWords(s: String): Int64 {
    let parts = collectArrayList(s.split(" ").iterator())
    var c = 0
    for (p in parts) {
        if (!(p.isEmpty())) {
            c += 1
        }
    }
    return c
}

func digitCount(s: String): Int64 {
    var c = 0
    for (ch in s.runes()) {
        if (ch.isAsciiNumber()) {
            c += 1
        }
    }
    return c
}

func letterCount(s: String): Int64 {
    var c = 0
    for (ch in s.runes()) {
        if (ch.isAsciiLetter()) {
            c += 1
        }
    }
    return c
}

func caesarShift(s: String, shift: Int64): String {
    let sb = StringBuilder()
    for (ch in s.runes()) {
        if ((ch >= r'a') && (ch <= r'z')) {
            let base = Int64(UInt32(r'a'))
            let v = ((Int64(UInt32(ch)) - base) + shift) % 26
            sb.append(Rune(UInt32((base + v))))
        } else {
            sb.append(ch)
        }
    }
    return sb.toString()
}

func acronym(s: String): String {
    let sb = StringBuilder()
    for (w in collectArrayList(s.split(" ").iterator())) {
        if (!(w.isEmpty())) {
            sb.append(w[0..1].toAsciiUpper())
        }
    }
    return sb.toString()
}

func sumList(xs: ArrayList<Int64>): Int64 {
    var s = 0
    for (x in xs) {
        s += x
    }
    return s
}

func maxList(xs: ArrayList<Int64>): Int64 {
    var m = xs[0]
    for (x in xs) {
        if (x > m) {
            m = x
        }
    }
    return m
}

func minList(xs: ArrayList<Int64>): Int64 {
    var m = xs[0]
    for (x in xs) {
        if (x < m) {
            m = x
        }
    }
    return m
}

func averageInt(xs: ArrayList<Int64>): Int64 {
    return sumList(xs) / xs.size
}

func bubbleSort(input: ArrayList<Int64>): ArrayList<Int64> {
    let a = collectArrayList(input)
    var i = 0
    while (i < a.size) {
        var j = 0
        while (j < ((a.size - 1) - i)) {
            if (a[j] > a[j + 1]) {
                let t = a[j]
                a[j] = a[j + 1]
                a[j + 1] = t
            }
            j += 1
        }
        i += 1
    }
    return a
}

func selectionSort(input: ArrayList<Int64>): ArrayList<Int64> {
    let a = collectArrayList(input)
    var i = 0
    while (i < a.size) {
        var mi = i
        var j = i + 1
        while (j < a.size) {
            if (a[j] < a[mi]) {
                mi = j
            }
            j += 1
        }
        let t = a[i]
        a[i] = a[mi]
        a[mi] = t
        i += 1
    }
    return a
}

func binarySearch(sorted: ArrayList<Int64>, target: Int64): Int64 {
    var lo = 0
    var hi = sorted.size - 1
    while (lo <= hi) {
        let mid = (lo + hi) / 2
        if (sorted[mid] == target) {
            return mid
        }
        if (sorted[mid] < target) {
            lo = mid + 1
        } else {
            hi = mid - 1
        }
    }
    return -1
}

func countOccurrences(xs: ArrayList<Int64>, target: Int64): Int64 {
    var c = 0
    for (x in xs) {
        if (x == target) {
            c += 1
        }
    }
    return c
}

func frequencies(xs: ArrayList<Int64>): HashMap<Int64, Int64> {
    let m = HashMap<Int64, Int64>()
    for (x in xs) {
        m[x] = (m.get(x) ?? 0) + 1
    }
    return m
}

func dedup(xs: ArrayList<Int64>): ArrayList<Int64> {
    let seen = HashMap<Int64, Bool>()
    let out = ArrayList<Int64>()
    for (x in xs) {
        if (!(seen.get(x) ?? false)) {
            seen[x] = true
            out.add(x)
        }
    }
    return out
}

func rotateLeft(xs: ArrayList<Int64>, k: Int64): ArrayList<Int64> {
    let n = xs.size
    let out = ArrayList<Int64>()
    var i = 0
    while (i < n) {
        out.add(xs[(i + k) % n])
        i += 1
    }
    return out
}

func runningSum(xs: ArrayList<Int64>): ArrayList<Int64> {
    let out = ArrayList<Int64>()
    var acc = 0
    for (x in xs) {
        acc += x
        out.add(acc)
    }
    return out
}

@Derive[Equatable]
enum Suit <: ToString {
    | CLUBS | DIAMONDS | HEARTS | SPADES
    public func toString(): String {
    return match (this) {
                case CLUBS => "CLUBS"
            case DIAMONDS => "DIAMONDS"
            case HEARTS => "HEARTS"
            case SPADES => "SPADES"
}
    }
}

@Derive[Equatable]
enum Direction <: ToString {
    | NORTH | EAST | SOUTH | WEST
    public func toString(): String {
    return match (this) {
                case NORTH => "NORTH"
            case EAST => "EAST"
            case SOUTH => "SOUTH"
            case WEST => "WEST"
}
    }
}

func turnRight(d: Direction): Direction {
    return match (d) {
        case Direction.NORTH => Direction.EAST
        case Direction.EAST => Direction.SOUTH
        case Direction.SOUTH => Direction.WEST
        case Direction.WEST => Direction.NORTH}
}

class Point <: ToString {
    let x: Int64
    let y: Int64
    init(x: Int64, y: Int64) {
        this.x = x
        this.y = y
    }
    public func toString(): String {
        return "Point(x=${this.x}, y=${this.y})"
    }
}

func manhattan(a: Point, b: Point): Int64 {
    let dx = if (a.x > b.x) {
        a.x - b.x
    } else {
        b.x - a.x
    }
    let dy = if (a.y > b.y) {
        a.y - b.y
    } else {
        b.y - a.y
    }
    return dx + dy
}

class Rect <: ToString {
    let w: Int64
    let h: Int64
    init(w: Int64, h: Int64) {
        this.w = w
        this.h = h
    }
    public func toString(): String {
        return "Rect(w=${this.w}, h=${this.h})"
    }
}

func area(r: Rect): Int64 {
    return r.w * r.h
}

open class Expr {}

class Num <: Expr {
    let value: Int64
    init(value: Int64) {
        this.value = value
    }
}

class Add <: Expr {
    let left: Expr
    let right: Expr
    init(left: Expr, right: Expr) {
        this.left = left
        this.right = right
    }
}

class Mul <: Expr {
    let left: Expr
    let right: Expr
    init(left: Expr, right: Expr) {
        this.left = left
        this.right = right
    }
}

class Neg <: Expr {
    let inner: Expr
    init(inner: Expr) {
        this.inner = inner
    }
}

func evalExpr(e: Expr): Int64 {
    return match (e) {
        case e: Num => e.value
        case e: Add => evalExpr(e.left) + evalExpr(e.right)
        case e: Mul => evalExpr(e.left) * evalExpr(e.right)
        case e: Neg => -evalExpr(e.inner)
        case _ => 0}
}

interface Shape {
    func area(): Int64
    func name(): String
}

class Square <: Shape {
    let side: Int64
    init(side: Int64) {
        this.side = side
    }
    public override func area(): Int64 {
        return side * side
    }
    public override func name(): String {
        return "Square"
    }
}

class Rectangle <: Shape {
    let w: Int64
    let h: Int64
    init(w: Int64, h: Int64) {
        this.w = w
        this.h = h
    }
    public override func area(): Int64 {
        return w * h
    }
    public override func name(): String {
        return "Rectangle"
    }
}

abstract class Animal {
    let name: String
    init(name: String) {
        this.name = name
    }
    public func sound(): String
    public open func describe(): String {
        return (name + " says ") + sound().toString()
    }
}

class Dog <: Animal {
    init(name: String) {
        super(name)
    }
    public override func sound(): String {
        return "Woof"
    }
}

class Cat <: Animal {
    init(name: String) {
        super(name)
    }
    public override func sound(): String {
        return "Meow"
    }
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
    func peek(): T {
        return items[items.size - 1]
    }
    func isEmpty(): Bool {
        return items.size == 0
    }
    func size(): Int64 {
        return items.size
    }
}

class Counter {
    var count = 0
    func inc() {
        count += 1
    }
    func add(n: Int64) {
        count += n
    }
    func get(): Int64 {
        return count
    }
}

func makeMatrix(rows: Int64, cols: Int64): ArrayList<ArrayList<Int64>> {
    let m = ArrayList<ArrayList<Int64>>()
    var i = 0
    while (i < rows) {
        let row = ArrayList<Int64>()
        var j = 0
        while (j < cols) {
            row.add((i * cols) + j)
            j += 1
        }
        m.add(row)
        i += 1
    }
    return m
}

func matrixTrace(m: ArrayList<ArrayList<Int64>>): Int64 {
    var s = 0
    var i = 0
    while (i < m.size) {
        s += m[i][i]
        i += 1
    }
    return s
}

func matrixSum(m: ArrayList<ArrayList<Int64>>): Int64 {
    var s = 0
    for (row in m) {
        for (v in row) {
            s += v
        }
    }
    return s
}

func transpose(m: ArrayList<ArrayList<Int64>>): ArrayList<ArrayList<Int64>> {
    let rows = m.size
    let cols = m[0].size
    let out = ArrayList<ArrayList<Int64>>()
    var j = 0
    while (j < cols) {
        let row = ArrayList<Int64>()
        var i = 0
        while (i < rows) {
            row.add(m[i][j])
            i += 1
        }
        out.add(row)
        j += 1
    }
    return out
}

func rowMaxes(m: ArrayList<ArrayList<Int64>>): ArrayList<Int64> {
    let out = ArrayList<Int64>()
    for (row in m) {
        var mx = row[0]
        for (v in row) {
            if (v > mx) {
                mx = v
            }
        }
        out.add(mx)
    }
    return out
}

func collatzSteps(start: Int64): Int64 {
    var n = start
    var steps = 0
    while (n != 1) {
        if ((n % 2) == 0) {
            n /= 2
        } else {
            n = (3 * n) + 1
        }
        steps += 1
    }
    return steps
}

func sumOfDigitsFactorial(n: Int64): Int64 {
    var x = n
    var s = 0
    while (x > 0) {
        s += factorial(x % 10)
        x /= 10
    }
    return s
}

func nthPrime(n: Int64): Int64 {
    var count = 0
    var candidate = 1
    while (count < n) {
        candidate += 1
        if (isPrime(candidate)) {
            count += 1
        }
    }
    return candidate
}

func gcdList(xs: ArrayList<Int64>): Int64 {
    var g = xs[0]
    for (x in xs) {
        g = gcd(g, x)
    }
    return g
}

func isArmstrong(n: Int64): Bool {
    let digits = ArrayList<Int64>()
    var x = n
    while (x > 0) {
        digits.add(x % 10)
        x /= 10
    }
    let p = digits.size
    var s = 0
    for (d in digits) {
        s += Int64(power(d, p))
    }
    return s == n
}

class Student <: ToString {
    let name: String
    let score: Int64
    init(name: String, score: Int64) {
        this.name = name
        this.score = score
    }
    public func toString(): String {
        return "Student(name=${this.name}, score=${this.score})"
    }
}

func grade(score: Int64): String {
    return if (score >= 90 && score <= 100) {
        "A"
    } else if (score >= 80 && score <= 89) {
        "B"
    } else if (score >= 70 && score <= 79) {
        "C"
    } else if (score >= 60 && score <= 69) {
        "D"
    } else {
        "F"
    }
}

func classAverage(students: ArrayList<Student>): Int64 {
    var s = 0
    for (st in students) {
        s += st.score
    }
    return s / students.size
}

func topStudent(students: ArrayList<Student>): Student {
    var best = students[0]
    for (st in students) {
        if (st.score > best.score) {
            best = st
        }
    }
    return best
}

func passCount(students: ArrayList<Student>, threshold: Int64): Int64 {
    var c = 0
    for (st in students) {
        if (st.score >= threshold) {
            c += 1
        }
    }
    return c
}

class Account <: ToString {
    let id: Int64
    var balance: Int64
    init(id: Int64, balance: Int64) {
        this.id = id
        this.balance = balance
    }
    public func toString(): String {
        return "Account(id=${this.id}, balance=${this.balance})"
    }
}

func deposit(acc: Account, amount: Int64): Account {
    acc.balance += amount
    return acc
}

func withdraw(acc: Account, amount: Int64): Bool {
    if (acc.balance >= amount) {
        acc.balance -= amount
        return true
    }
    return false
}

func totalBalance(accounts: ArrayList<Account>): Int64 {
    var s = 0
    for (a in accounts) {
        s += a.balance
    }
    return s
}

func wordFrequency(text: String): HashMap<String, Int64> {
    let m = HashMap<String, Int64>()
    for (w in collectArrayList(text.split(" ").iterator())) {
        if (!(w.isEmpty())) {
            m[w] = (m.get(w) ?? 0) + 1
        }
    }
    return m
}

func longestWord(text: String): String {
    var best = ""
    for (w in collectArrayList(text.split(" ").iterator())) {
        if (w.size > best.size) {
            best = w
        }
    }
    return best
}

func titleCase(text: String): String {
    let out = ArrayList<String>()
    for (w in collectArrayList(text.split(" ").iterator())) {
        if (!(w.isEmpty())) {
            out.add(toUpperFirst(w))
        }
    }
    return String.join(collectArray<String>(out.iterator().map({e => e.toString()})), delimiter: " ")
}

func countSentences(text: String): Int64 {
    var c = 0
    for (ch in text.runes()) {
        if (((ch == r'.') || (ch == r'!')) || (ch == r'?')) {
            c += 1
        }
    }
    return c
}

func evalRpn(tokens: ArrayList<String>): Int64 {
    let stack = Stack<Int64>()
    for (tok in tokens) {
        if ((((tok == "+") || (tok == "-")) || (tok == "*")) || (tok == "/")) {
            let b = stack.pop()
            let a = stack.pop()
            let r = match (tok) {
                case "+" => a + b
                case "-" => a - b
                case "*" => a * b
                case _ => a / b}
            stack.push(r)
        } else {
            stack.push(Int64.parse(tok))
        }
    }
    return stack.pop()
}

func toBinary(n: Int64): String {
    if (n == 0) {
        return "0"
    }
    var x = n
    let sb = StringBuilder()
    while (x > 0) {
        sb.append((x % 2).toString())
        x /= 2
    }
    return reverseString(sb.toString())
}

func toHex(n: Int64): String {
    if (n == 0) {
        return "0"
    }
    let digits = "0123456789abcdef"
    var x = n
    let sb = StringBuilder()
    while (x > 0) {
        sb.append(digits.toRuneArray()[x % 16])
        x /= 16
    }
    return reverseString(sb.toString())
}

func fromBinary(s: String): Int64 {
    var r = 0
    for (ch in s.runes()) {
        r = (r * 2) + (Int64(UInt32(ch)) - Int64(UInt32(r'0')))
    }
    return r
}

func combinations(n: Int64, k: Int64): Int64 {
    if ((k < 0) || (k > n)) {
        return 0
    }
    var num = 1
    var den = 1
    var i = 0
    while (i < k) {
        num *= n - i
        den *= i + 1
        i += 1
    }
    return num / den
}

func permutations(n: Int64, k: Int64): Int64 {
    var r = 1
    var i = 0
    while (i < k) {
        r *= n - i
        i += 1
    }
    return r
}

func sumOfSquares(n: Int64): Int64 {
    var s = 0
    var i = 1
    while (i <= n) {
        s += i * i
        i += 1
    }
    return s
}

func triangular(n: Int64): Int64 {
    return (n * (n + 1)) / 2
}

class Queue<T> {
    let items = ArrayList<T>()
    func enqueue(x: T) {
        items.add(x)
    }
    func dequeue(): T {
        let x = items[0]
        items.remove(at: 0)
        return x
    }
    func isEmpty(): Bool {
        return items.size == 0
    }
    func size(): Int64 {
        return items.size
    }
}

func makeRange(lo: Int64, hi: Int64): ArrayList<Int64> {
    let out = ArrayList<Int64>()
    var i = lo
    while (i <= hi) {
        out.add(i)
        i += 1
    }
    return out
}

func zipSum(a: ArrayList<Int64>, b: ArrayList<Int64>): ArrayList<Int64> {
    let out = ArrayList<Int64>()
    var i = 0
    let n = if (a.size < b.size) {
        a.size
    } else {
        b.size
    }
    while (i < n) {
        out.add(a[i] + b[i])
        i += 1
    }
    return out
}

func dotProduct(a: ArrayList<Int64>, b: ArrayList<Int64>): Int64 {
    var s = 0
    var i = 0
    while (i < a.size) {
        s += a[i] * b[i]
        i += 1
    }
    return s
}

class Item <: ToString {
    let name: String
    let price: Int64
    var qty: Int64
    init(name: String, price: Int64, qty: Int64) {
        this.name = name
        this.price = price
        this.qty = qty
    }
    public func toString(): String {
        return "Item(name=${this.name}, price=${this.price}, qty=${this.qty})"
    }
}

func inventoryValue(items: ArrayList<Item>): Int64 {
    var s = 0
    for (it in items) {
        s += it.price * it.qty
    }
    return s
}

func lowStock(items: ArrayList<Item>, threshold: Int64): ArrayList<String> {
    let out = ArrayList<String>()
    for (it in items) {
        if (it.qty < threshold) {
            out.add(it.name)
        }
    }
    return out
}

func restock(items: ArrayList<Item>, amount: Int64) {
    for (it in items) {
        it.qty += amount
    }
}

func priciest(items: ArrayList<Item>): Item {
    var best = items[0]
    for (it in items) {
        if (it.price > best.price) {
            best = it
        }
    }
    return best
}

@Derive[Equatable]
enum TrafficLight <: ToString {
    | RED | GREEN | YELLOW
    public func toString(): String {
    return match (this) {
                case RED => "RED"
            case GREEN => "GREEN"
            case YELLOW => "YELLOW"
}
    }
}

func nextLight(t: TrafficLight): TrafficLight {
    return match (t) {
        case TrafficLight.RED => TrafficLight.GREEN
        case TrafficLight.GREEN => TrafficLight.YELLOW
        case TrafficLight.YELLOW => TrafficLight.RED}
}

func lightDuration(t: TrafficLight): Int64 {
    return match (t) {
        case TrafficLight.RED => 30
        case TrafficLight.GREEN => 25
        case TrafficLight.YELLOW => 5}
}

main() {
    println("== math ==")
    println(gcd(48, 36))
    println(lcm(4, 6))
    println(String.join(collectArray<String>(primesUpTo(30).iterator().map({e => e.toString()})), delimiter: ","))
    println(factorial(6))
    println(fib(15))
    println(power(2, 16))
    println(digitSum(987654))
    println(reverseInt(12300))
    println(isPalindromeInt(1221))
    println(clampInt(15, 0, 10))
    println(maxOfThree(3, 9, 5))
    println(minOfThree(3, 9, 5))
    println(sumRange(1, 100))
    println(countDivisors(36))
    println(isPerfect(28))
    println(isPerfect(12))
    println("== strings ==")
    println(reverseString("translator"))
    println(isPalindrome("racecar"))
    println(isPalindrome("hello"))
    println(countVowels("the quick brown fox"))
    println(countChar("mississippi", r's'))
    println(toUpperFirst("kotlin"))
    println(repeatString("xy", 4))
    println(countWords("  spaced   out  words "))
    println(digitCount("ab12cd34ef"))
    println(letterCount("ab12cd34ef"))
    println(caesarShift("hello", 3))
    println(acronym("portable network graphics"))
    println("== collections ==")
    let data = ArrayList([5, 2, 8, 1, 9, 3, 7, 4, 6, 2, 8])
    println(sumList(data))
    println(maxList(data))
    println(minList(data))
    println(averageInt(data))
    println(String.join(collectArray<String>(bubbleSort(data).iterator().map({e => e.toString()})), delimiter: ","))
    println(String.join(collectArray<String>(selectionSort(data).iterator().map({e => e.toString()})), delimiter: ","))
    let sortedData = bubbleSort(data)
    println(binarySearch(sortedData, 7))
    println(countOccurrences(data, 8))
    println(String.join(collectArray<String>(dedup(data).iterator().map({e => e.toString()})), delimiter: ","))
    println(String.join(collectArray<String>(rotateLeft(ArrayList([1, 2, 3, 4, 5]), 2).iterator().map({e => e.toString()})), delimiter: ","))
    println(String.join(collectArray<String>(runningSum(ArrayList([1, 2, 3, 4])).iterator().map({e => e.toString()})), delimiter: ","))
    let freq = frequencies(data)
    for (k in ({ => let _s = collectArrayList(freq.keys().iterator()); sort(_s, stable: true); _s })()) {
        println((k.toString() + ":") + freq[k].toString())
    }
    println("== functional ==")
    let nums = ArrayList([10, 15, 20, 25, 30, 35, 40])
    println(String.join(collectArray<String>(collectArrayList(nums.iterator().filter({ it => (it % 10) == 0 })).iterator().map({e => e.toString()})), delimiter: ","))
    println(String.join(collectArray<String>(collectArrayList(nums.iterator().map({ it => it / 5 })).iterator().map({e => e.toString()})), delimiter: ","))
    println(String.join(collectArray<String>(collectArrayList(collectArrayList(nums.iterator().filter({ it => it > 20 })).iterator().map({ it => it * 2 })).iterator().map({e => e.toString()})), delimiter: ","))
    println(nums.iterator().fold<Int64>(0, {acc, x => acc + x}))
    println(nums.iterator().filter({ it => it > 20 }).count())
    println(nums.iterator().any({ it => it > 35 }))
    println(nums.iterator().all({ it => it > 5 }))
    println(String.join(collectArray<String>(collectArrayList(({ => let _s = collectArrayList(nums.iterator()); sort(_s, stable: true, descending: true); _s })().iterator().take(3)).iterator().map({e => e.toString()})), delimiter: ","))
    println("== enums ==")
    println(turnRight(Direction.NORTH))
    println(turnRight(Direction.WEST))
    var d = Direction.NORTH
    var steps = 0
    while (steps < 6) {
        d = turnRight(d)
        steps += 1
    }
    println(d)
    println("== data classes ==")
    let p1 = Point(1, 2)
    let p2 = Point(4, 6)
    println(p1)
    println(manhattan(p1, p2))
    println(area(Rect(3, 5)))
    println("== expr ==")
    let expr = Add(Num(3), Mul(Num(4), Num(5)))
    println(evalExpr(expr))
    println(evalExpr(Neg(Num(7))))
    let expr2 = Mul(Add(Num(1), Num(2)), Add(Num(3), Num(4)))
    println(evalExpr(expr2))
    println("== shapes ==")
    let shapes = ArrayList<Shape>([Square(4), Rectangle(3, 6), Square(2)])
    for (s in shapes) {
        println((s.name().toString() + ":") + s.area().toString())
    }
    var totalArea = 0
    for (s in shapes) {
        totalArea += s.area()
    }
    println(totalArea)
    println("== animals ==")
    let animals = ArrayList<Animal>([Dog("Rex"), Cat("Felix")])
    for (a in animals) {
        println(a.describe())
    }
    println("== stack ==")
    let stk = Stack<Int64>()
    stk.push(10)
    stk.push(20)
    stk.push(30)
    println(stk.size())
    println(stk.peek())
    println(stk.pop())
    println(stk.pop())
    println(stk.size())
    println("== counter ==")
    let counter = Counter()
    counter.inc()
    counter.inc()
    counter.add(10)
    println(counter.get())
    println("== matrix ==")
    let mat = makeMatrix(3, 3)
    println(matrixTrace(mat))
    println(matrixSum(mat))
    println(String.join(collectArray<String>(rowMaxes(mat).iterator().map({e => e.toString()})), delimiter: ","))
    let tr = transpose(mat)
    println(String.join(collectArray<String>(tr[0].iterator().map({e => e.toString()})), delimiter: ","))
    println("== number theory ==")
    println(collatzSteps(27))
    println(nthPrime(10))
    println(gcdList(ArrayList([24, 36, 48])))
    println(isArmstrong(153))
    println(isArmstrong(154))
    println("== grading ==")
    let students = ArrayList([Student("Alice", 92), Student("Bob", 78), Student("Carol", 85), Student("Dave", 55), Student("Eve", 67)])
    for (st in students) {
        println((st.name.toString() + ":") + grade(st.score).toString())
    }
    println(classAverage(students))
    println(topStudent(students).name)
    println(passCount(students, 60))
    println("== bank ==")
    let accounts = ArrayList([Account(1, 100), Account(2, 250), Account(3, 50)])
    deposit(accounts[0], 50)
    println(withdraw(accounts[1], 100))
    println(withdraw(accounts[2], 200))
    println(totalBalance(accounts))
    println("== text ==")
    let text = "the cat sat on the mat the cat ran"
    let wf = wordFrequency(text)
    for (k in ({ => let _s = collectArrayList(wf.keys().iterator()); sort(_s, stable: true); _s })()) {
        println((k.toString() + ":") + wf[k].toString())
    }
    println(longestWord("a bb ccc dddd ee"))
    println(titleCase("hello world from kotlin"))
    println(countSentences("Hi! How are you? I am fine."))
    println("== rpn ==")
    println(evalRpn(ArrayList(["3", "4", "+", "5", "*"])))
    println(evalRpn(ArrayList(["10", "2", "8", "*", "+", "3", "-"])))
    println("== base & combinatorics ==")
    println(toBinary(42))
    println(toHex(255))
    println(fromBinary("101010"))
    println(combinations(10, 3))
    println(permutations(5, 2))
    println(sumOfSquares(5))
    println(triangular(10))
    println("== queue ==")
    let q = Queue<String>()
    q.enqueue("a")
    q.enqueue("b")
    q.enqueue("c")
    println(q.size())
    println(q.dequeue())
    println(q.dequeue())
    println(q.size())
    println("== vectors ==")
    let va = makeRange(1, 5)
    let vb = makeRange(6, 10)
    println(String.join(collectArray<String>(zipSum(va, vb).iterator().map({e => e.toString()})), delimiter: ","))
    println(dotProduct(va, vb))
    println("== inventory ==")
    let items = ArrayList([Item("pen", 2, 100), Item("notebook", 5, 3), Item("eraser", 1, 50), Item("marker", 4, 2)])
    println(inventoryValue(items))
    println(String.join(collectArray<String>(lowStock(items, 10).iterator().map({e => e.toString()})), delimiter: ","))
    restock(items, 5)
    println(inventoryValue(items))
    println(priciest(items).name)
    println("== traffic ==")
    var light = TrafficLight.RED
    var cycle = 0
    var totalDuration = 0
    while (cycle < 6) {
        totalDuration += lightDuration(light)
        light = nextLight(light)
        cycle += 1
    }
    println(totalDuration)
    println(light)
    println("done")
}
