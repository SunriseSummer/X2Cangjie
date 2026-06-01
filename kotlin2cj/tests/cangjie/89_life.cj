import std.collection.*

class Grid {
    let rows: Int64
    let cols: Int64
    init(rows: Int64, cols: Int64) {
        this.rows = rows
        this.cols = cols
        for (r in 0..rows) {
            let row = ArrayList<Bool>()
            for (c in 0..cols) {
                row.add(false)
            }
            cells.add(row)
        }
    }
    let cells = ArrayList<ArrayList<Bool>>()
    func set(r: Int64, c: Int64, v: Bool) {
        cells[r][c] = v
    }
    func get(r: Int64, c: Int64): Bool {
        if ((((r < 0) || (r >= rows)) || (c < 0)) || (c >= cols)) {
            return false
        }
        return cells[r][c]
    }
    func liveNeighbors(r: Int64, c: Int64): Int64 {
        var count = 0
        for (dr in -1..=1) {
            for (dc in -1..=1) {
                if ((dr == 0) && (dc == 0)) {
                    continue
                }
                if (get(r + dr, c + dc)) {
                    count = count + 1
                }
            }
        }
        return count
    }
    func step(): Grid {
        let next = Grid(rows, cols)
        for (r in 0..rows) {
            for (c in 0..cols) {
                let n = liveNeighbors(r, c)
                let alive = get(r, c)
                if (alive && ((n == 2) || (n == 3))) {
                    next.set(r, c, true)
                } else if (!alive && (n == 3)) {
                    next.set(r, c, true)
                }
            }
        }
        return next
    }
    func population(): Int64 {
        var count = 0
        for (r in 0..rows) {
            for (c in 0..cols) {
                if (cells[r][c]) {
                    count = count + 1
                }
            }
        }
        return count
    }
    func render(): String {
        let sb = StringBuilder()
        for (r in 0..rows) {
            for (c in 0..cols) {
                if (cells[r][c]) {
                    sb.append("*")
                } else {
                    sb.append(".")
                }
            }
            sb.append("\n")
        }
        return sb.toString()
    }
}

main() {
    let g = Grid(5, 5)
    g.set(2, 1, true)
    g.set(2, 2, true)
    g.set(2, 3, true)
    println("=== Generation 0 ===")
    print(g.render())
    println("Population: ${g.population()}")
    var cur = g
    let history = ArrayList<Int64>()
    history.add(cur.population())
    for (gen in 1..=4) {
        cur = cur.step()
        history.add(cur.population())
        println("=== Generation ${gen} ===")
        print(cur.render())
        println("Population: ${cur.population()}")
    }
    println("=== Population history ===")
    println(String.join(collectArray<String>(history.iterator().map({e => e.toString()})), delimiter: " -> "))
    println("Peak: ${history.iterator().reduce({a, b => if (a > b) { a } else { b }}) ?? 0}")
    println("Total over time: ${history.iterator().fold<Int64>(0, {acc, x => acc + x})}")
    let big = Grid(6, 6)
    big.set(0, 1, true)
    big.set(1, 2, true)
    big.set(2, 0, true)
    big.set(2, 1, true)
    big.set(2, 2, true)
    println("=== Glider start (pop ${big.population()}) ===")
    var gg = big
    for (gen in 1..=3) {
        gg = gg.step()
    }
    println("After 3 steps, population: ${gg.population()}")
    print(gg.render())
}
