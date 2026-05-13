import std.collection.*

main(): Unit {
    var xs = ArrayList<Int64>([1, 2, 3, 4, 5])
    var total = 0
    for (x in xs) {
        total += x
    }
    println(total)
    return 0
}
