import std.collection.*

func transpose(m: ArrayList<ArrayList<Int64>>): ArrayList<ArrayList<Int64>> {
    let rows = m.size
    let cols = m[0].size
    let out = ArrayList<ArrayList<Int64>>()
    for (_ in 0..cols) {
        let row = ArrayList<Int64>()
        for (_ in 0..rows) {
            row.add(0)
        }
        out.add(row)
    }
    for (i in 0..rows) {
        for (j in 0..cols) {
            out[j][i] = m[i][j]
        }
    }
    return out
}

main() {
    let m = ArrayList<ArrayList<Int64>>([
        ArrayList<Int64>([1, 2, 3]),
        ArrayList<Int64>([4, 5, 6])
    ])
    let t = transpose(m)
    for (row in t) {
        for (v in row) {
            println(v)
        }
    }
    return 0
}
