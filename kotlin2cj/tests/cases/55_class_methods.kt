class Counter(var value: Int) {
    fun inc() {
        value += 1
    }
    fun add(n: Int) {
        value += n
    }
    fun isEven(): Boolean {
        return value % 2 == 0
    }
}
fun main() {
    val c = Counter(0)
    c.inc()
    c.inc()
    c.add(5)
    println("value=${c.value}")
    println("even=${c.isEven()}")
    c.inc()
    println("even=${c.isEven()}")
}
