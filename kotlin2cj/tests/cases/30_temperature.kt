fun classify(t: Int): String {
    return when {
        t < 0 -> "freezing"
        t < 15 -> "cold"
        t < 25 -> "mild"
        else -> "hot"
    }
}
fun main() {
    val temps = mutableListOf(-5, 10, 20, 30)
    for (t in temps) {
        println("$t: ${classify(t)}")
    }
}
