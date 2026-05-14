// Large #2 (iter9): seat allocation grid with row summaries
class SeatMap {
    let rows: Int
    let cols: Int
    var seats: [[Bool]] = []
    init(_ rows: Int, _ cols: Int) {
        self.rows = rows
        self.cols = cols
        var r = 0
        while r < rows {
            var row: [Bool] = []
            var c = 0
            while c < cols { row.append(false); c += 1 }
            seats.append(row)
            r += 1
        }
    }
    func reserve(_ r: Int, _ c: Int) -> Bool {
        if r < 0 || r >= rows || c < 0 || c >= cols { return false }
        if seats[r][c] { return false }
        seats[r][c] = true
        return true
    }
    func freeInRow(_ r: Int) -> Int {
        var n = 0
        var c = 0
        while c < cols {
            if !seats[r][c] { n += 1 }
            c += 1
        }
        return n
    }
    func firstFree() -> (Int, Int) {
        var r = 0
        while r < rows {
            var c = 0
            while c < cols {
                if !seats[r][c] { return (r, c) }
                c += 1
            }
            r += 1
        }
        return (-1, -1)
    }
    func render() -> String {
        var s = ""
        var r = 0
        while r < rows {
            var c = 0
            while c < cols {
                if seats[r][c] { s = s + "X" } else { s = s + "." }
                c += 1
            }
            s = s + " free=" + "\(freeInRow(r))" + "\n"
            r += 1
        }
        return s
    }
}

let sm = SeatMap(3, 5)
let reqs = [(0,0), (0,1), (1,3), (2,4), (1,3), (2,0)]
for q in reqs {
    print("reserve \(q.0),\(q.1)=\(sm.reserve(q.0, q.1))")
}
let f = sm.firstFree()
print("first=\(f.0),\(f.1)")
print(sm.render())
