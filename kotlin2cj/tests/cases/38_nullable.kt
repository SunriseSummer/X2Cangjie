fun describe(name: String?): String {
    return name ?: "unknown"
}
fun main() {
    val a: String? = null
    val b: String? = "Kotlin"
    println(describe(a))
    println(describe(b))
    println(a ?: "none")
}
