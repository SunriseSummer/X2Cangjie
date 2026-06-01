fun main() {
    val greeting by lazy { "Hello" + " " + "World" }
    println(greeting)

    val computed by lazy {
        val x = 10
        val y = 20
        x + y
    }
    println(computed)

    val items by lazy { mutableListOf(1, 2, 3) }
    println(items.size)
}
