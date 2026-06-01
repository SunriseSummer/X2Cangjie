fun divmod(a: Int, b: Int): Pair<Int, Int> = Pair(a / b, a % b)

fun main() {
    val (q, r) = divmod(17, 5)
    println("$q $r")
    val point = 3 to 7
    val (x, y) = point
    println(x + y)
    val pairs = listOf(1 to "one", 2 to "two", 3 to "three")
    for ((n, name) in pairs) {
        println("$n=$name")
    }
}
