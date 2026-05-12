// Medium #2: matrix operations (~100 lines)
class Matrix {
    let rows: Int
    let cols: Int
    var data: [Int] = []

    init(rows: Int, cols: Int) {
        self.rows = rows
        self.cols = cols
        for _ in 0 ..< (rows * cols) {
            data.append(0)
        }
    }

    func set(r: Int, c: Int, v: Int) {
        data[r * cols + c] = v
    }

    func get(r: Int, c: Int) -> Int {
        return data[r * cols + c]
    }

    func fillSequential() {
        var v = 1
        for r in 0 ..< rows {
            for c in 0 ..< cols {
                set(r: r, c: c, v: v)
                v += 1
            }
        }
    }

    func transpose() -> Matrix {
        let m = Matrix(rows: cols, cols: rows)
        for r in 0 ..< rows {
            for c in 0 ..< cols {
                m.set(r: c, c: r, v: get(r: r, c: c))
            }
        }
        return m
    }

    func multiply(_ other: Matrix) -> Matrix {
        let m = Matrix(rows: rows, cols: other.cols)
        for i in 0 ..< rows {
            for j in 0 ..< other.cols {
                var s = 0
                for k in 0 ..< cols {
                    s += get(r: i, c: k) * other.get(r: k, c: j)
                }
                m.set(r: i, c: j, v: s)
            }
        }
        return m
    }

    func printAll() {
        for r in 0 ..< rows {
            var line = ""
            for c in 0 ..< cols {
                line = line + " " + "\(get(r: r, c: c))"
            }
            print(line)
        }
    }

    func trace() -> Int {
        var s = 0
        var i = 0
        let n = (rows < cols) ? rows : cols
        while i < n {
            s += get(r: i, c: i)
            i += 1
        }
        return s
    }
}

let m = Matrix(rows: 3, cols: 4)
m.fillSequential()
m.printAll()
print("---")
let t = m.transpose()
t.printAll()
print("---")
let s = Matrix(rows: 3, cols: 3)
s.set(r: 0, c: 0, v: 1)
s.set(r: 1, c: 1, v: 2)
s.set(r: 2, c: 2, v: 3)
print("trace = \(s.trace())")
let p = m.multiply(t)
p.printAll()
