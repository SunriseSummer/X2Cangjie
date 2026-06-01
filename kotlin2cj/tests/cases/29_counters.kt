class Counter(var value: Int) {
    fun inc() {
        value += 1
    }
}
fun main() {
    val counters = mutableListOf(Counter(0), Counter(10), Counter(20))
    for (c in counters) {
        c.inc()
        c.inc()
    }
    var total = 0
    for (c in counters) {
        total += c.value
    }
    println("total=$total")
}
