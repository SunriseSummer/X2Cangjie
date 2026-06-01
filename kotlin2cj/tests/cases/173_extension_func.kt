// Test: Extension functions
fun Int.isPositive(): Boolean = this > 0
fun Int.square(): Int = this * this
fun String.addBrackets(): String = "[$this]"

fun main() {
    println("5.isPositive: ${5.isPositive()}")
    val neg = -3
    println("-3.isPositive: ${neg.isPositive()}")
    println("4.square: ${4.square()}")
    println("Hello.addBrackets: ${"Hello".addBrackets()}")

    val list = arrayListOf(10, 20, 30)
    println("list size: ${list.size}")
}
