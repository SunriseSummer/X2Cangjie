import std.collection.*

let xs: ArrayList<Int64> = ArrayList<Int64>([3, 1, 4, 1, 5, 9, 2, 6])

var total: Int64 = 0

main() {
    for (x in xs) {
        total = total + x
    }
    println("total=${total}")
    return 0
}
