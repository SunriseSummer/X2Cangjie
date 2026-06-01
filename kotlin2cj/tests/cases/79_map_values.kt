fun main() {
    val scores = mapOf("Alice" to 90, "Bob" to 85, "Carol" to 95)
    for ((name, score) in scores) {
        println("$name: $score")
    }
    val total = scores.values.sum()
    println("total=$total")
    println("Bob=${scores["Bob"]}")
}
