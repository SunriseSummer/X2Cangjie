import std.collection.*

main() {
    let text = "the cat sat on the mat the cat ran"
    let words = collectArrayList(text.split(" ").iterator())
    let counts = HashMap<String, Int64>()
    for (w in words) {
        counts[w] = (counts.get(w) ?? 0) + 1
    }
    let keys = ArrayList(["the", "cat", "sat", "on", "mat", "ran"])
    for (k in keys) {
        println("${k}: ${counts.get(k) ?? 0}")
    }
}
