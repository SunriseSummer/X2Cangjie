fun main() {
    for (n in 1..5) {
        val name = when (n) {
            1 -> "one"
            2, 3 -> "few"
            else -> "many"
        }
        println("$n -> $name")
    }
}
