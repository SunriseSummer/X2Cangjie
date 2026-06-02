import std.collection.*
import std.sort.*

main() {
    let map = HashMap([("a", 1), ("b", 2), ("c", 3)])
    let keys = ArrayList<String>()
    let values = ArrayList<Int64>()
    for ((k, v) in map) {
        keys.add(k)
        values.add(v)
    }
    sort(keys, stable: true)
    println("Keys: ${String.join(collectArray<String>(keys.iterator().map({e => e.toString()})), delimiter: ", ")}")
    let scores = HashMap<Int64, String>()
    scores[1] = "Alice"
    scores[2] = "Bob"
    scores[3] = "Charlie"
    let result = StringBuilder()
    let entries = ArrayList<Int64>()
    for ((id, name) in scores) {
        entries.add(id)
    }
    sort(entries, stable: true)
    for (id in entries) {
        let name = scores[id]
        if ((result.toString().size > 0)) {
            result.append("; ")
        }
        result.append("${id}=${name}")
    }
    println(result.toString())
    var total = 0
    for ((_, v) in map) {
        total += v
    }
    println("Total: ${total}")
}
