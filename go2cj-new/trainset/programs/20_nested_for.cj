import std.collection.*

main() {
    var matrix = ArrayList<ArrayList<Int64>>([
        ArrayList<Int64>([1, 2, 3]),
        ArrayList<Int64>([4, 5, 6])
    ])
    for (row in matrix) {
        var sum = 0
        for (v in row) {
            sum += v
        }
        println(sum)
    }
    return 0
}
