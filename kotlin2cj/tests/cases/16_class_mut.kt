class Counter(var value: Int) {
    fun inc() {
        value += 1
    }
    fun add(n: Int) {
        value += n
    }
}
fun main() {
    val c = Counter(0)
    c.inc()
    c.inc()
    c.add(10)
    println("value=${c.value}")
}
