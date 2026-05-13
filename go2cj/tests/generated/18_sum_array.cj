import std.collection.*

func sum(xs: ArrayList<Int64>): Int64 {
    var s = 0
    for (v in xs) {
        s += v
    }
    return s
}

main() {
    var xs = ArrayList<Int64>([1, 2, 3, 4, 5])
    println(sum(xs))
    return 0
}
