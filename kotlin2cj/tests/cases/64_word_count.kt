fun main() {
    val text = "the cat sat on the mat the cat ran"
    val words = text.split(" ")
    val counts = HashMap<String, Int>()
    for (w in words) {
        counts[w] = (counts[w] ?: 0) + 1
    }
    val keys = listOf("the", "cat", "sat", "on", "mat", "ran")
    for (k in keys) {
        println("$k: ${counts[k] ?: 0}")
    }
}
