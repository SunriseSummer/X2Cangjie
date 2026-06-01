fun classify(x: Int): String {
    return when {
        x in 0..9 -> "small"
        x in 10..99 -> "medium"
        else -> "large"
    }
}
fun main() {
    for (v in listOf(3, 42, 500)) {
        println(classify(v))
    }
    val score = 75
    println(score in 60..100)
    println(score !in 0..59)
    val xs = listOf(1, 2, 3)
    println(2 in xs)
    println(9 !in xs)
}
