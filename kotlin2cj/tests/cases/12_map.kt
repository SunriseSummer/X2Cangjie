fun main() {
    val scores = mutableMapOf("alice" to 90, "bob" to 85)
    scores["carol"] = 95
    println("alice=${scores["alice"]}")
    println("carol=${scores["carol"]}")
    println("size=${scores.size}")
}
