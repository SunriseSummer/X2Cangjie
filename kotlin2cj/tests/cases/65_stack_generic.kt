class IntStack {
    val items = ArrayList<Int>()
    fun push(x: Int) {
        items.add(x)
    }
    fun pop(): Int {
        val top = items.last()
        items.removeAt(items.size - 1)
        return top
    }
    fun isEmpty(): Boolean = items.isEmpty()
    fun size(): Int = items.size
}

fun main() {
    val st = IntStack()
    for (i in 1..5) {
        st.push(i * i)
    }
    println(st.size())
    var sum = 0
    while (!st.isEmpty()) {
        sum = sum + st.pop()
    }
    println(sum)
}
