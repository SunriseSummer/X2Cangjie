class IntStack {
    val items = mutableListOf<Int>()
    fun push(x: Int) {
        items.add(x)
    }
    fun size(): Int {
        return items.size
    }
    fun top(): Int {
        return items[items.size - 1]
    }
}
fun main() {
    val s = IntStack()
    s.push(10)
    s.push(20)
    s.push(30)
    println("size=${s.size()} top=${s.top()}")
}
