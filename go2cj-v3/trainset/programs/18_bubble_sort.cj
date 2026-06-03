import std.collection.*

func bubbleSort(xs: ArrayList<Int64>): Unit {
    let n = xs.size
    for (i in 0..n-1) {
        for (j in 0..n-1-i) {
            if (xs[j] > xs[j+1]) {
                let t = xs[j]
                xs[j] = xs[j+1]
                xs[j+1] = t
            }
        }
    }
}

main() {
    var xs = ArrayList<Int64>([5, 2, 4, 1, 3])
    bubbleSort(xs)
    for (v in xs) {
        println(v)
    }
    return 0
}
