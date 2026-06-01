// Nested generic collections and complex type interactions
fun main() {
    // ArrayList of ArrayLists (2D)
    val grid = ArrayList<ArrayList<Int>>()
    for (i in 0..2) {
        val row = ArrayList<Int>()
        for (j in 0..2) {
            row.add(i * 3 + j + 1)
        }
        grid.add(row)
    }
    for (row in grid) {
        println(row.joinToString(" "))
    }

    // HashMap with ArrayList values
    val groups = HashMap<String, ArrayList<Int>>()
    groups["even"] = arrayListOf(2, 4, 6)
    groups["odd"] = arrayListOf(1, 3, 5)
    for ((key, vals) in groups) {
        val sorted = ArrayList<Int>()
        for (v in vals) sorted.add(v)
        sorted.sort()
        println("$key: ${sorted.joinToString(", ")}")
    }

    // Nested iteration with index tracking
    var total = 0
    for (i in 0 until grid.size) {
        for (j in 0 until grid[i].size) {
            total += grid[i][j]
        }
    }
    println("Grid sum: $total")
}
