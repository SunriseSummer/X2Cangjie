import std.collection.*

main() {
    let scores = HashMap([("alice", 90), ("bob", 85)])
    scores["carol"] = 95
    println("alice=${scores["alice"]}")
    println("carol=${scores["carol"]}")
    println("size=${scores.size}")
}
