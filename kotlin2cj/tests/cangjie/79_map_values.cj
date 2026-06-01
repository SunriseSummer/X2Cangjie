import std.collection.*

main() {
    let scores = HashMap([("Alice", 90), ("Bob", 85), ("Carol", 95)])
    for ((name, score) in scores) {
        println("${name}: ${score}")
    }
    let total = scores.values().iterator().fold<Int64>(0, {acc, x => acc + x})
    println("total=${total}")
    println("Bob=${scores["Bob"]}")
}
