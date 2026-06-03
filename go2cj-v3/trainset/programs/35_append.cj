import std.collection.*

main() {
    var xs = ArrayList<Int64>([1, 2, 3])
    xs.add(4)
    xs.add(5)
    for (v in xs) {
        println(v)
    }
    return 0
}
