import std.collection.*

main() {
    var xs = ArrayList<Int64>([5, 3, 8, 1, 9, 2])
    var maxv = xs[0]
    for (v in xs) {
        if (v > maxv) {
            maxv = v
        }
    }
    println(maxv)
    return 0
}
