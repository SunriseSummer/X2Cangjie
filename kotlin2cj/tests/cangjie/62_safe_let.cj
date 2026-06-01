import std.collection.*

main() {
    let scores = HashMap([("alice", 90), ("bob", 75)])
    if (let Some(it) <- scores.get("alice")) {
        println("alice: ${it}")
    }
    if (let Some(it) <- scores.get("carol")) {
        println("carol: ${it}")
    }
    let name: ?String = "kotlin"
    if (let Some(it) <- name) {
        println(it.size)
    }
    let missing: ?String = None
    if (let Some(it) <- missing) {
        println("should not print")
    }
    println("done")
}
