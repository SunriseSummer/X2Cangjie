// Iterator pattern with custom iteration
class RangeIterator(val start: Int, val endExclusive: Int, val step: Int) {
    var current: Int

    init {
        current = start
    }

    fun hasNext(): Boolean {
        return if (step > 0) current < endExclusive else current > endExclusive
    }

    fun next(): Int {
        val v = current
        current += step
        return v
    }
}

class FibIterator(val limit: Int) {
    var a = 0
    var b = 1
    var count = 0

    fun hasNext(): Boolean = count < limit

    fun next(): Int {
        val result = a
        val tmp = a + b
        a = b
        b = tmp
        count++
        return result
    }
}

fun collectRange(start: Int, end: Int, step: Int): ArrayList<Int> {
    val result = ArrayList<Int>()
    val iter = RangeIterator(start, end, step)
    while (iter.hasNext()) {
        result.add(iter.next())
    }
    return result
}

fun collectFib(n: Int): ArrayList<Int> {
    val result = ArrayList<Int>()
    val iter = FibIterator(n)
    while (iter.hasNext()) {
        result.add(iter.next())
    }
    return result
}

fun main() {
    // Range iterator
    val r1 = collectRange(0, 10, 2)
    println(r1.joinToString(" "))

    val r2 = collectRange(10, 0, -3)
    println(r2.joinToString(" "))

    val r3 = collectRange(1, 6, 1)
    println(r3.joinToString(" "))

    // Fibonacci iterator
    val fib = collectFib(10)
    println(fib.joinToString(" "))

    val fib5 = collectFib(5)
    println(fib5.joinToString(" "))
}
