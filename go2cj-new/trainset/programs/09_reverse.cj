import std.collection.*

func reverse(xs: ArrayList<Int64>): ArrayList<Int64> {
    var n = xs.size
    var out = ArrayList<Int64>()
    for (i in 0..n) {
        out.add(xs[n - 1 - i])
    }
    return out
}

main() {
    var r = reverse(ArrayList<Int64>([1, 2, 3, 4, 5]))
    for (v in r) {
        println(v)
    }
    return 0
}
