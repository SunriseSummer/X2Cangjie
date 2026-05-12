import std.collection.*

let m: HashMap<String, Int64> = HashMap<String, Int64>([("a", 1), ("b", 2), ("c", 3)])

main() {
    println(m["a"])
    println(m["b"])
    println(m["c"])
    return 0
}
