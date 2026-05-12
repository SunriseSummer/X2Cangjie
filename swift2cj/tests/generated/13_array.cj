import std.collection.*

var xs: ArrayList<Int64> = ArrayList<Int64>([1, 2, 3, 4, 5])

var s: Int64 = 0

main() {
    xs.add(6)
    for (v in xs) {
        s = s + v
    }
    println(s)
    println(xs.size)
    return 0
}
