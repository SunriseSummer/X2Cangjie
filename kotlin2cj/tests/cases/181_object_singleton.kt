object Counter {
    var count = 0
    fun increment() {
        count++
    }
    fun getCount(): Int = count
}

fun main() {
    Counter.increment()
    Counter.increment()
    Counter.increment()
    println(Counter.getCount())
    println(Counter.count)
}
