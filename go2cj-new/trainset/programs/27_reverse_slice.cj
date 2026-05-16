import std.collection.*

main() {
    var xs = ArrayList<Int64>([1, 2, 3, 4, 5])
    var r = ArrayList<Int64>()
    var i = xs.size - 1
    while (i >= 0) {
        r.add(xs[i])
        i -= 1
    }
    for (v in r) {
        println(v)
    }
    return 0
}
