import std.collection.*

func quicksort(xs: ArrayList<Int64>, lo: Int64, hi: Int64): Unit {
    if (lo >= hi) {
        return
    }
    var pivot = xs[hi]
    var i = lo
    for (j in lo..hi) {
        if (xs[j] < pivot) {
            var tmp = xs[i]
            xs[i] = xs[j]
            xs[j] = tmp
            i += 1
        }
    }
    var tmp = xs[i]
    xs[i] = xs[hi]
    xs[hi] = tmp
    quicksort(xs, lo, i - 1)
    quicksort(xs, i + 1, hi)
}

main() {
    var xs = ArrayList<Int64>([5, 2, 8, 1, 9, 3, 7, 4, 6])
    quicksort(xs, 0, xs.size - 1)
    for (v in xs) {
        println(v)
    }
    return 0
}
