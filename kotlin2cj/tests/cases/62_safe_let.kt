fun main() {
    val scores = mapOf("alice" to 90, "bob" to 75)
    scores["alice"]?.let { println("alice: $it") }
    scores["carol"]?.let { println("carol: $it") }
    val name: String? = "kotlin"
    name?.let { println(it.length) }
    val missing: String? = null
    missing?.let { println("should not print") }
    println("done")
}
