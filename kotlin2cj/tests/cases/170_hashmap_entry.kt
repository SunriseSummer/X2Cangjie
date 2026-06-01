// Test: HashMap entry iteration with destructuring
fun main() {
    val map = hashMapOf("a" to 1, "b" to 2, "c" to 3)

    // Destructure iteration
    val keys = ArrayList<String>()
    val values = ArrayList<Int>()
    for ((k, v) in map) {
        keys.add(k)
        values.add(v)
    }
    keys.sort()
    println("Keys: ${keys.joinToString(", ")}")

    // HashMap with Int keys
    val scores = HashMap<Int, String>()
    scores[1] = "Alice"
    scores[2] = "Bob"
    scores[3] = "Charlie"

    val result = StringBuilder()
    val entries = ArrayList<Int>()
    for ((id, name) in scores) {
        entries.add(id)
    }
    entries.sort()
    for (id in entries) {
        val name = scores[id]!!
        if (result.isNotEmpty()) result.append("; ")
        result.append("$id=$name")
    }
    println(result.toString())

    // Count with destructuring
    var total = 0
    for ((_, v) in map) {
        total += v
    }
    println("Total: $total")
}
