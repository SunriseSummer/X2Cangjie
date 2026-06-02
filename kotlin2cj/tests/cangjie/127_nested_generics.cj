import std.collection.*
import std.sort.*

main() {
    let grid = ArrayList<ArrayList<Int64>>()
    for (i in 0..=2) {
        let row = ArrayList<Int64>()
        for (j in 0..=2) {
            row.add(((i * 3) + j) + 1)
        }
        grid.add(row)
    }
    for (row in grid) {
        println(String.join(collectArray<String>(row.iterator().map({e => e.toString()})), delimiter: " "))
    }
    let groups = HashMap<String, ArrayList<Int64>>()
    groups["even"] = ArrayList([2, 4, 6])
    groups["odd"] = ArrayList([1, 3, 5])
    for ((key, vals) in groups) {
        let sorted = ArrayList<Int64>()
        for (v in vals) {
            sorted.add(v)
        }
        sort(sorted, stable: true)
        println("${key}: ${String.join(collectArray<String>(sorted.iterator().map({e => e.toString()})), delimiter: ", ")}")
    }
    var total = 0
    for (i in 0..grid.size) {
        for (j in 0..grid[i].size) {
            total += grid[i][j]
        }
    }
    println("Grid sum: ${total}")
}
