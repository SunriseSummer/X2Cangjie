fun sign(x: Int): String {
    val s = when {
        x > 0 -> "positive"
        x < 0 -> "negative"
        else -> "zero"
    }
    return s
}
fun main() {
    println(sign(7))
    println(sign(-3))
    println(sign(0))
}
