import std.collection.*

main() {
    let grid = ArrayList<ArrayList<Int64>>()
    for (r in 0..=2) {
        let row = ArrayList<Int64>()
        for (c in 0..=2) {
            row.add((r * 3) + c)
        }
        grid.add(row)
    }
    var sum = 0
    for (row in grid) {
        for (v in row) {
            sum += v
        }
    }
    println("sum=${sum}")
    println("grid[1][2]=${grid[1][2]}")
    let groups = HashMap<String, ArrayList<Int64>>()
    for (i in 1..=6) {
        let key = if ((i % 2) == 0) {
            "even"
        } else {
            "odd"
        }
        if (!groups.contains(key)) {
            groups[key] = ArrayList<Int64>()
        }
        groups[key].add(i)
    }
    var evenCount = 0
    for (v in groups["even"]) {
        evenCount += 1
    }
    println("even count=${evenCount}")
}
