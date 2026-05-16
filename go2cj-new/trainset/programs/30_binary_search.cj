import std.collection.*

func search(xs: ArrayList<Int64>, target: Int64): Int64 {
    var lo = 0
    var hi = xs.size - 1
    while (lo <= hi) {
        var mid = (lo + hi) / 2
        if (xs[mid] == target) {
            return mid
        }
        if (xs[mid] < target) {
            lo = mid + 1
        } else {
            hi = mid - 1
        }
    }
    return -1
}

main() {
    var xs = ArrayList<Int64>([1, 3, 5, 7, 9, 11])
    println(search(xs, 7))
    println(search(xs, 4))
    return 0
}
