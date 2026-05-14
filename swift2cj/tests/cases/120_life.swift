// Large #2 (iter7): Conway-style grid evolution
class Grid {
    let h: Int
    let w: Int
    var cells: [[Int]] = []

    init(_ h: Int, _ w: Int) {
        self.h = h
        self.w = w
        var r = 0
        while r < h {
            var row: [Int] = []
            var c = 0
            while c < w {
                row.append(0)
                c += 1
            }
            cells.append(row)
            r += 1
        }
    }

    func set(_ r: Int, _ c: Int, _ v: Int) {
        cells[r][c] = v
    }

    func get(_ r: Int, _ c: Int) -> Int {
        if r < 0 || r >= h || c < 0 || c >= w {
            return 0
        }
        return cells[r][c]
    }

    func neighbors(_ r: Int, _ c: Int) -> Int {
        var total = 0
        var dr = -1
        while dr <= 1 {
            var dc = -1
            while dc <= 1 {
                if !(dr == 0 && dc == 0) {
                    total += get(r + dr, c + dc)
                }
                dc += 1
            }
            dr += 1
        }
        return total
    }

    func step() -> Grid {
        let g = Grid(h, w)
        var r = 0
        while r < h {
            var c = 0
            while c < w {
                let n = neighbors(r, c)
                let alive = get(r, c) == 1
                if alive {
                    if n == 2 || n == 3 {
                        g.set(r, c, 1)
                    }
                } else {
                    if n == 3 {
                        g.set(r, c, 1)
                    }
                }
                c += 1
            }
            r += 1
        }
        return g
    }

    func show() -> String {
        var s = ""
        var r = 0
        while r < h {
            var c = 0
            while c < w {
                if cells[r][c] == 1 {
                    s = s + "#"
                } else {
                    s = s + "."
                }
                c += 1
            }
            s = s + "\n"
            r += 1
        }
        return s
    }
}

var g = Grid(5, 5)
g.set(1, 2, 1)
g.set(2, 2, 1)
g.set(3, 2, 1)
print("start")
print(g.show())
var i = 1
while i <= 4 {
    g = g.step()
    print("step \(i)")
    print(g.show())
    i += 1
}
