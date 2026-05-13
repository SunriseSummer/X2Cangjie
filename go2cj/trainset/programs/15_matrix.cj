import std.collection.*

main() {
    var matrix = ArrayList<ArrayList<Int64>>([
        ArrayList<Int64>([1, 2, 3]),
        ArrayList<Int64>([4, 5, 6]),
        ArrayList<Int64>([7, 8, 9])
    ])
    var total = 0
    for (row in matrix) {
        for (v in row) {
            total += v
        }
    }
    println(total)
    return 0
}
