import std.collection.*

main() {
    var xs = ArrayList<Int64>([10, 20, 30])
    for ((i, v) in xs.iterator().enumerate()) {
        println("${i} ${v}")
    }
    return 0
}
