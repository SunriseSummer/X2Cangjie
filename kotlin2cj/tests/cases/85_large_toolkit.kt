// ===== Section 1: math utilities =====
fun gcd(a: Int, b: Int): Int {
    var x = a
    var y = b
    while (y != 0) {
        val t = y
        y = x % y
        x = t
    }
    return x
}

fun lcm(a: Int, b: Int): Int = a / gcd(a, b) * b

fun isPrime(n: Int): Boolean {
    if (n < 2) return false
    var i = 2
    while (i * i <= n) {
        if (n % i == 0) return false
        i += 1
    }
    return true
}

fun primesUpTo(n: Int): List<Int> {
    val result = mutableListOf<Int>()
    var i = 2
    while (i <= n) {
        if (isPrime(i)) result.add(i)
        i += 1
    }
    return result
}

fun factorial(n: Int): Long {
    var r = 1L
    var i = 2
    while (i <= n) {
        r *= i
        i += 1
    }
    return r
}

fun fib(n: Int): Long {
    if (n < 2) return n.toLong()
    var a = 0L
    var b = 1L
    var i = 2
    while (i <= n) {
        val c = a + b
        a = b
        b = c
        i += 1
    }
    return b
}

fun power(base: Int, exp: Int): Long {
    var r = 1L
    var i = 0
    while (i < exp) {
        r *= base
        i += 1
    }
    return r
}

fun digitSum(n: Int): Int {
    var x = if (n < 0) -n else n
    var s = 0
    while (x > 0) {
        s += x % 10
        x /= 10
    }
    return s
}

fun reverseInt(n: Int): Int {
    var x = if (n < 0) -n else n
    var r = 0
    while (x > 0) {
        r = r * 10 + x % 10
        x /= 10
    }
    return if (n < 0) -r else r
}

fun isPalindromeInt(n: Int): Boolean = n == reverseInt(n)

fun clampInt(v: Int, lo: Int, hi: Int): Int {
    if (v < lo) return lo
    if (v > hi) return hi
    return v
}

fun maxOfThree(a: Int, b: Int, c: Int): Int {
    var m = a
    if (b > m) m = b
    if (c > m) m = c
    return m
}

fun minOfThree(a: Int, b: Int, c: Int): Int {
    var m = a
    if (b < m) m = b
    if (c < m) m = c
    return m
}

fun sumRange(lo: Int, hi: Int): Int {
    var s = 0
    var i = lo
    while (i <= hi) {
        s += i
        i += 1
    }
    return s
}

fun countDivisors(n: Int): Int {
    var cnt = 0
    var i = 1
    while (i <= n) {
        if (n % i == 0) cnt += 1
        i += 1
    }
    return cnt
}

fun isPerfect(n: Int): Boolean {
    var s = 0
    var i = 1
    while (i < n) {
        if (n % i == 0) s += i
        i += 1
    }
    return s == n
}

// ===== Section 2: string utilities =====
fun reverseString(s: String): String {
    val sb = StringBuilder()
    var i = s.length - 1
    while (i >= 0) {
        sb.append(s[i])
        i -= 1
    }
    return sb.toString()
}

fun isPalindrome(s: String): Boolean {
    var i = 0
    var j = s.length - 1
    while (i < j) {
        if (s[i] != s[j]) return false
        i += 1
        j -= 1
    }
    return true
}

fun countVowels(s: String): Int {
    var c = 0
    for (ch in s) {
        if (ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u') c += 1
    }
    return c
}

fun countChar(s: String, target: Char): Int {
    var c = 0
    for (ch in s) {
        if (ch == target) c += 1
    }
    return c
}

fun toUpperFirst(s: String): String {
    if (s.isEmpty()) return s
    return s.substring(0, 1).uppercase() + s.substring(1)
}

fun repeatString(s: String, n: Int): String {
    val sb = StringBuilder()
    var i = 0
    while (i < n) {
        sb.append(s)
        i += 1
    }
    return sb.toString()
}

fun countWords(s: String): Int {
    val parts = s.split(" ")
    var c = 0
    for (p in parts) {
        if (p.isNotEmpty()) c += 1
    }
    return c
}

fun digitCount(s: String): Int {
    var c = 0
    for (ch in s) {
        if (ch.isDigit()) c += 1
    }
    return c
}

fun letterCount(s: String): Int {
    var c = 0
    for (ch in s) {
        if (ch.isLetter()) c += 1
    }
    return c
}

fun caesarShift(s: String, shift: Int): String {
    val sb = StringBuilder()
    for (ch in s) {
        if (ch >= 'a' && ch <= 'z') {
            val base = 'a'.code
            val v = (ch.code - base + shift) % 26
            sb.append((base + v).toChar())
        } else {
            sb.append(ch)
        }
    }
    return sb.toString()
}

fun acronym(s: String): String {
    val sb = StringBuilder()
    for (w in s.split(" ")) {
        if (w.isNotEmpty()) sb.append(w.substring(0, 1).uppercase())
    }
    return sb.toString()
}


// ===== Section 3: collection utilities =====
fun sumList(xs: List<Int>): Int {
    var s = 0
    for (x in xs) s += x
    return s
}

fun maxList(xs: List<Int>): Int {
    var m = xs[0]
    for (x in xs) {
        if (x > m) m = x
    }
    return m
}

fun minList(xs: List<Int>): Int {
    var m = xs[0]
    for (x in xs) {
        if (x < m) m = x
    }
    return m
}

fun averageInt(xs: List<Int>): Int = sumList(xs) / xs.size

fun bubbleSort(input: List<Int>): List<Int> {
    val a = input.toMutableList()
    var i = 0
    while (i < a.size) {
        var j = 0
        while (j < a.size - 1 - i) {
            if (a[j] > a[j + 1]) {
                val t = a[j]
                a[j] = a[j + 1]
                a[j + 1] = t
            }
            j += 1
        }
        i += 1
    }
    return a
}

fun selectionSort(input: List<Int>): List<Int> {
    val a = input.toMutableList()
    var i = 0
    while (i < a.size) {
        var mi = i
        var j = i + 1
        while (j < a.size) {
            if (a[j] < a[mi]) mi = j
            j += 1
        }
        val t = a[i]
        a[i] = a[mi]
        a[mi] = t
        i += 1
    }
    return a
}

fun binarySearch(sorted: List<Int>, target: Int): Int {
    var lo = 0
    var hi = sorted.size - 1
    while (lo <= hi) {
        val mid = (lo + hi) / 2
        if (sorted[mid] == target) return mid
        if (sorted[mid] < target) lo = mid + 1
        else hi = mid - 1
    }
    return -1
}

fun countOccurrences(xs: List<Int>, target: Int): Int {
    var c = 0
    for (x in xs) {
        if (x == target) c += 1
    }
    return c
}

fun frequencies(xs: List<Int>): Map<Int, Int> {
    val m = mutableMapOf<Int, Int>()
    for (x in xs) {
        m[x] = (m[x] ?: 0) + 1
    }
    return m
}

fun dedup(xs: List<Int>): List<Int> {
    val seen = mutableMapOf<Int, Boolean>()
    val out = mutableListOf<Int>()
    for (x in xs) {
        if (!(seen[x] ?: false)) {
            seen[x] = true
            out.add(x)
        }
    }
    return out
}

fun rotateLeft(xs: List<Int>, k: Int): List<Int> {
    val n = xs.size
    val out = mutableListOf<Int>()
    var i = 0
    while (i < n) {
        out.add(xs[(i + k) % n])
        i += 1
    }
    return out
}

fun runningSum(xs: List<Int>): List<Int> {
    val out = mutableListOf<Int>()
    var acc = 0
    for (x in xs) {
        acc += x
        out.add(acc)
    }
    return out
}

// ===== Section 4: enums, data classes, sealed =====
enum class Suit { CLUBS, DIAMONDS, HEARTS, SPADES }

enum class Direction { NORTH, EAST, SOUTH, WEST }

fun turnRight(d: Direction): Direction = when (d) {
    Direction.NORTH -> Direction.EAST
    Direction.EAST -> Direction.SOUTH
    Direction.SOUTH -> Direction.WEST
    Direction.WEST -> Direction.NORTH
}

data class Point(val x: Int, val y: Int)

fun manhattan(a: Point, b: Point): Int {
    val dx = if (a.x > b.x) a.x - b.x else b.x - a.x
    val dy = if (a.y > b.y) a.y - b.y else b.y - a.y
    return dx + dy
}

data class Rect(val w: Int, val h: Int)

fun area(r: Rect): Int = r.w * r.h

sealed class Expr
class Num(val value: Int) : Expr()
class Add(val left: Expr, val right: Expr) : Expr()
class Mul(val left: Expr, val right: Expr) : Expr()
class Neg(val inner: Expr) : Expr()

fun evalExpr(e: Expr): Int = when (e) {
    is Num -> e.value
    is Add -> evalExpr(e.left) + evalExpr(e.right)
    is Mul -> evalExpr(e.left) * evalExpr(e.right)
    is Neg -> -evalExpr(e.inner)
    else -> 0
}

// ===== Section 5: interfaces & abstract classes =====
interface Shape {
    fun area(): Int
    fun name(): String
}

class Square(val side: Int) : Shape {
    override fun area(): Int = side * side
    override fun name(): String = "Square"
}

class Rectangle(val w: Int, val h: Int) : Shape {
    override fun area(): Int = w * h
    override fun name(): String = "Rectangle"
}

abstract class Animal(val name: String) {
    abstract fun sound(): String
    fun describe(): String = name + " says " + sound()
}

class Dog(name: String) : Animal(name) {
    override fun sound(): String = "Woof"
}

class Cat(name: String) : Animal(name) {
    override fun sound(): String = "Meow"
}

// ===== Section 6: generic containers =====
class Stack<T> {
    val items = mutableListOf<T>()
    fun push(x: T) {
        items.add(x)
    }
    fun pop(): T {
        val x = items[items.size - 1]
        items.removeAt(items.size - 1)
        return x
    }
    fun peek(): T = items[items.size - 1]
    fun isEmpty(): Boolean = items.size == 0
    fun size(): Int = items.size
}

class Counter {
    var count = 0
    fun inc() {
        count += 1
    }
    fun add(n: Int) {
        count += n
    }
    fun get(): Int = count
}

// ===== Section 7: matrix / 2D =====
fun makeMatrix(rows: Int, cols: Int): List<List<Int>> {
    val m = mutableListOf<List<Int>>()
    var i = 0
    while (i < rows) {
        val row = mutableListOf<Int>()
        var j = 0
        while (j < cols) {
            row.add(i * cols + j)
            j += 1
        }
        m.add(row)
        i += 1
    }
    return m
}

fun matrixTrace(m: List<List<Int>>): Int {
    var s = 0
    var i = 0
    while (i < m.size) {
        s += m[i][i]
        i += 1
    }
    return s
}

fun matrixSum(m: List<List<Int>>): Int {
    var s = 0
    for (row in m) {
        for (v in row) s += v
    }
    return s
}

fun transpose(m: List<List<Int>>): List<List<Int>> {
    val rows = m.size
    val cols = m[0].size
    val out = mutableListOf<List<Int>>()
    var j = 0
    while (j < cols) {
        val row = mutableListOf<Int>()
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

fun rowMaxes(m: List<List<Int>>): List<Int> {
    val out = mutableListOf<Int>()
    for (row in m) {
        var mx = row[0]
        for (v in row) {
            if (v > mx) mx = v
        }
        out.add(mx)
    }
    return out
}

// ===== Section 8: number theory =====
fun collatzSteps(start: Int): Int {
    var n = start
    var steps = 0
    while (n != 1) {
        if (n % 2 == 0) n /= 2
        else n = 3 * n + 1
        steps += 1
    }
    return steps
}

fun sumOfDigitsFactorial(n: Int): Long {
    var x = n
    var s = 0L
    while (x > 0) {
        s += factorial(x % 10)
        x /= 10
    }
    return s
}

fun nthPrime(n: Int): Int {
    var count = 0
    var candidate = 1
    while (count < n) {
        candidate += 1
        if (isPrime(candidate)) count += 1
    }
    return candidate
}

fun gcdList(xs: List<Int>): Int {
    var g = xs[0]
    for (x in xs) g = gcd(g, x)
    return g
}

fun isArmstrong(n: Int): Boolean {
    val digits = mutableListOf<Int>()
    var x = n
    while (x > 0) {
        digits.add(x % 10)
        x /= 10
    }
    val p = digits.size
    var s = 0
    for (d in digits) {
        s += power(d, p).toInt()
    }
    return s == n
}

// ===== Section 9: grading & stats =====
data class Student(val name: String, val score: Int)

fun grade(score: Int): String = when (score) {
    in 90..100 -> "A"
    in 80..89 -> "B"
    in 70..79 -> "C"
    in 60..69 -> "D"
    else -> "F"
}

fun classAverage(students: List<Student>): Int {
    var s = 0
    for (st in students) s += st.score
    return s / students.size
}

fun topStudent(students: List<Student>): Student {
    var best = students[0]
    for (st in students) {
        if (st.score > best.score) best = st
    }
    return best
}

fun passCount(students: List<Student>, threshold: Int): Int {
    var c = 0
    for (st in students) {
        if (st.score >= threshold) c += 1
    }
    return c
}

// ===== Section 10: bank domain =====
data class Account(val id: Int, var balance: Int)

fun deposit(acc: Account, amount: Int): Account {
    acc.balance += amount
    return acc
}

fun withdraw(acc: Account, amount: Int): Boolean {
    if (acc.balance >= amount) {
        acc.balance -= amount
        return true
    }
    return false
}

fun totalBalance(accounts: List<Account>): Int {
    var s = 0
    for (a in accounts) s += a.balance
    return s
}

// ===== Section 11: text processing =====
fun wordFrequency(text: String): Map<String, Int> {
    val m = mutableMapOf<String, Int>()
    for (w in text.split(" ")) {
        if (w.isNotEmpty()) m[w] = (m[w] ?: 0) + 1
    }
    return m
}

fun longestWord(text: String): String {
    var best = ""
    for (w in text.split(" ")) {
        if (w.length > best.length) best = w
    }
    return best
}

fun titleCase(text: String): String {
    val out = mutableListOf<String>()
    for (w in text.split(" ")) {
        if (w.isNotEmpty()) out.add(toUpperFirst(w))
    }
    return out.joinToString(" ")
}

fun countSentences(text: String): Int {
    var c = 0
    for (ch in text) {
        if (ch == '.' || ch == '!' || ch == '?') c += 1
    }
    return c
}

// ===== Section 12: simple stack machine (RPN) =====
fun evalRpn(tokens: List<String>): Int {
    val stack = Stack<Int>()
    for (tok in tokens) {
        if (tok == "+" || tok == "-" || tok == "*" || tok == "/") {
            val b = stack.pop()
            val a = stack.pop()
            val r = when (tok) {
                "+" -> a + b
                "-" -> a - b
                "*" -> a * b
                else -> a / b
            }
            stack.push(r)
        } else {
            stack.push(tok.toInt())
        }
    }
    return stack.pop()
}

// ===== Section 13: base conversion & combinatorics =====
fun toBinary(n: Int): String {
    if (n == 0) return "0"
    var x = n
    val sb = StringBuilder()
    while (x > 0) {
        sb.append((x % 2).toString())
        x /= 2
    }
    return reverseString(sb.toString())
}

fun toHex(n: Int): String {
    if (n == 0) return "0"
    val digits = "0123456789abcdef"
    var x = n
    val sb = StringBuilder()
    while (x > 0) {
        sb.append(digits[x % 16])
        x /= 16
    }
    return reverseString(sb.toString())
}

fun fromBinary(s: String): Int {
    var r = 0
    for (ch in s) {
        r = r * 2 + (ch.code - '0'.code)
    }
    return r
}

fun combinations(n: Int, k: Int): Long {
    if (k < 0 || k > n) return 0L
    var num = 1L
    var den = 1L
    var i = 0
    while (i < k) {
        num *= (n - i)
        den *= (i + 1)
        i += 1
    }
    return num / den
}

fun permutations(n: Int, k: Int): Long {
    var r = 1L
    var i = 0
    while (i < k) {
        r *= (n - i)
        i += 1
    }
    return r
}

fun sumOfSquares(n: Int): Int {
    var s = 0
    var i = 1
    while (i <= n) {
        s += i * i
        i += 1
    }
    return s
}

fun triangular(n: Int): Int = n * (n + 1) / 2

// ===== Section 14: generic queue & pair utils =====
class Queue<T> {
    val items = mutableListOf<T>()
    fun enqueue(x: T) {
        items.add(x)
    }
    fun dequeue(): T {
        val x = items[0]
        items.removeAt(0)
        return x
    }
    fun isEmpty(): Boolean = items.size == 0
    fun size(): Int = items.size
}

fun makeRange(lo: Int, hi: Int): List<Int> {
    val out = mutableListOf<Int>()
    var i = lo
    while (i <= hi) {
        out.add(i)
        i += 1
    }
    return out
}

fun zipSum(a: List<Int>, b: List<Int>): List<Int> {
    val out = mutableListOf<Int>()
    var i = 0
    val n = if (a.size < b.size) a.size else b.size
    while (i < n) {
        out.add(a[i] + b[i])
        i += 1
    }
    return out
}

fun dotProduct(a: List<Int>, b: List<Int>): Int {
    var s = 0
    var i = 0
    while (i < a.size) {
        s += a[i] * b[i]
        i += 1
    }
    return s
}

// ===== Section 15: inventory domain =====
data class Item(val name: String, val price: Int, var qty: Int)

fun inventoryValue(items: List<Item>): Int {
    var s = 0
    for (it in items) s += it.price * it.qty
    return s
}

fun lowStock(items: List<Item>, threshold: Int): List<String> {
    val out = mutableListOf<String>()
    for (it in items) {
        if (it.qty < threshold) out.add(it.name)
    }
    return out
}

fun restock(items: List<Item>, amount: Int) {
    for (it in items) {
        it.qty += amount
    }
}

fun priciest(items: List<Item>): Item {
    var best = items[0]
    for (it in items) {
        if (it.price > best.price) best = it
    }
    return best
}

// ===== Section 16: simple state machine =====
enum class TrafficLight { RED, GREEN, YELLOW }

fun nextLight(t: TrafficLight): TrafficLight = when (t) {
    TrafficLight.RED -> TrafficLight.GREEN
    TrafficLight.GREEN -> TrafficLight.YELLOW
    TrafficLight.YELLOW -> TrafficLight.RED
}

fun lightDuration(t: TrafficLight): Int = when (t) {
    TrafficLight.RED -> 30
    TrafficLight.GREEN -> 25
    TrafficLight.YELLOW -> 5
}

fun main() {
    println("== math ==")
    println(gcd(48, 36))
    println(lcm(4, 6))
    println(primesUpTo(30).joinToString(","))
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
    println(countChar("mississippi", 's'))
    println(toUpperFirst("kotlin"))
    println(repeatString("xy", 4))
    println(countWords("  spaced   out  words "))
    println(digitCount("ab12cd34ef"))
    println(letterCount("ab12cd34ef"))
    println(caesarShift("hello", 3))
    println(acronym("portable network graphics"))

    println("== collections ==")
    val data = listOf(5, 2, 8, 1, 9, 3, 7, 4, 6, 2, 8)
    println(sumList(data))
    println(maxList(data))
    println(minList(data))
    println(averageInt(data))
    println(bubbleSort(data).joinToString(","))
    println(selectionSort(data).joinToString(","))
    val sortedData = bubbleSort(data)
    println(binarySearch(sortedData, 7))
    println(countOccurrences(data, 8))
    println(dedup(data).joinToString(","))
    println(rotateLeft(listOf(1, 2, 3, 4, 5), 2).joinToString(","))
    println(runningSum(listOf(1, 2, 3, 4)).joinToString(","))
    val freq = frequencies(data)
    for (k in freq.keys.sorted()) {
        println(k.toString() + ":" + freq[k])
    }

    println("== functional ==")
    val nums = listOf(10, 15, 20, 25, 30, 35, 40)
    println(nums.filter { it % 10 == 0 }.joinToString(","))
    println(nums.map { it / 5 }.joinToString(","))
    println(nums.filter { it > 20 }.map { it * 2 }.joinToString(","))
    println(nums.sum())
    println(nums.count { it > 20 })
    println(nums.any { it > 35 })
    println(nums.all { it > 5 })
    println(nums.sortedDescending().take(3).joinToString(","))

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
    val p1 = Point(1, 2)
    val p2 = Point(4, 6)
    println(p1)
    println(manhattan(p1, p2))
    println(area(Rect(3, 5)))

    println("== expr ==")
    val expr = Add(Num(3), Mul(Num(4), Num(5)))
    println(evalExpr(expr))
    println(evalExpr(Neg(Num(7))))
    val expr2 = Mul(Add(Num(1), Num(2)), Add(Num(3), Num(4)))
    println(evalExpr(expr2))

    println("== shapes ==")
    val shapes = listOf<Shape>(Square(4), Rectangle(3, 6), Square(2))
    for (s in shapes) {
        println(s.name() + ":" + s.area())
    }
    var totalArea = 0
    for (s in shapes) totalArea += s.area()
    println(totalArea)

    println("== animals ==")
    val animals = listOf<Animal>(Dog("Rex"), Cat("Felix"))
    for (a in animals) {
        println(a.describe())
    }

    println("== stack ==")
    val stk = Stack<Int>()
    stk.push(10)
    stk.push(20)
    stk.push(30)
    println(stk.size())
    println(stk.peek())
    println(stk.pop())
    println(stk.pop())
    println(stk.size())

    println("== counter ==")
    val counter = Counter()
    counter.inc()
    counter.inc()
    counter.add(10)
    println(counter.get())

    println("== matrix ==")
    val mat = makeMatrix(3, 3)
    println(matrixTrace(mat))
    println(matrixSum(mat))
    println(rowMaxes(mat).joinToString(","))
    val tr = transpose(mat)
    println(tr[0].joinToString(","))

    println("== number theory ==")
    println(collatzSteps(27))
    println(nthPrime(10))
    println(gcdList(listOf(24, 36, 48)))
    println(isArmstrong(153))
    println(isArmstrong(154))

    println("== grading ==")
    val students = listOf(
        Student("Alice", 92),
        Student("Bob", 78),
        Student("Carol", 85),
        Student("Dave", 55),
        Student("Eve", 67)
    )
    for (st in students) {
        println(st.name + ":" + grade(st.score))
    }
    println(classAverage(students))
    println(topStudent(students).name)
    println(passCount(students, 60))

    println("== bank ==")
    val accounts = listOf(Account(1, 100), Account(2, 250), Account(3, 50))
    deposit(accounts[0], 50)
    println(withdraw(accounts[1], 100))
    println(withdraw(accounts[2], 200))
    println(totalBalance(accounts))

    println("== text ==")
    val text = "the cat sat on the mat the cat ran"
    val wf = wordFrequency(text)
    for (k in wf.keys.sorted()) {
        println(k + ":" + wf[k])
    }
    println(longestWord("a bb ccc dddd ee"))
    println(titleCase("hello world from kotlin"))
    println(countSentences("Hi! How are you? I am fine."))

    println("== rpn ==")
    println(evalRpn(listOf("3", "4", "+", "5", "*")))
    println(evalRpn(listOf("10", "2", "8", "*", "+", "3", "-")))


    println("== base & combinatorics ==")
    println(toBinary(42))
    println(toHex(255))
    println(fromBinary("101010"))
    println(combinations(10, 3))
    println(permutations(5, 2))
    println(sumOfSquares(5))
    println(triangular(10))

    println("== queue ==")
    val q = Queue<String>()
    q.enqueue("a")
    q.enqueue("b")
    q.enqueue("c")
    println(q.size())
    println(q.dequeue())
    println(q.dequeue())
    println(q.size())

    println("== vectors ==")
    val va = makeRange(1, 5)
    val vb = makeRange(6, 10)
    println(zipSum(va, vb).joinToString(","))
    println(dotProduct(va, vb))

    println("== inventory ==")
    val items = listOf(
        Item("pen", 2, 100),
        Item("notebook", 5, 3),
        Item("eraser", 1, 50),
        Item("marker", 4, 2)
    )
    println(inventoryValue(items))
    println(lowStock(items, 10).joinToString(","))
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
