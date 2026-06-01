fun main() {
    val grid = mutableListOf<MutableList<Int>>()
    for (r in 0..2) {
        val row = mutableListOf<Int>()
        for (c in 0..2) {
            row.add(r * 3 + c)
        }
        grid.add(row)
    }
    var sum = 0
    for (row in grid) {
        for (v in row) {
            sum += v
        }
    }
    println("sum=$sum")
    println("grid[1][2]=${grid[1][2]}")

    val groups = mutableMapOf<String, MutableList<Int>>()
    for (i in 1..6) {
        val key = if (i % 2 == 0) "even" else "odd"
        if (!groups.contains(key)) {
            groups[key] = mutableListOf<Int>()
        }
        groups[key]!!.add(i)
    }
    var evenCount = 0
    for (v in groups["even"]!!) {
        evenCount += 1
    }
    println("even count=$evenCount")
}
