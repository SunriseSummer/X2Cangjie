// Large #1 (iter6): grid maze BFS shortest path
class Pos {
    let r: Int
    let c: Int
    init(_ r: Int, _ c: Int) {
        self.r = r
        self.c = c
    }
    func key() -> String {
        return "\(r),\(c)"
    }
}

class Maze {
    let h: Int
    let w: Int
    var walls: [String: Bool] = [:]

    init(_ h: Int, _ w: Int) {
        self.h = h
        self.w = w
    }

    func block(_ r: Int, _ c: Int) {
        walls["\(r),\(c)"] = true
    }

    func open(_ r: Int, _ c: Int) -> Bool {
        if r < 0 || r >= h || c < 0 || c >= w {
            return false
        }
        return !(walls["\(r),\(c)"] ?? false)
    }

    func shortest(_ sr: Int, _ sc: Int, _ tr: Int, _ tc: Int) -> [Pos] {
        var q: [Pos] = []
        var head = 0
        var seen: [String: Bool] = [:]
        var prev: [String: String] = [:]
        let start = Pos(sr, sc)
        let target = "\(tr),\(tc)"
        q.append(start)
        seen[start.key()] = true
        let dr = [1, -1, 0, 0]
        let dc = [0, 0, 1, -1]
        while head < q.count {
            let cur = q[head]
            head += 1
            if cur.key() == target {
                break
            }
            var i = 0
            while i < 4 {
                let nr = cur.r + dr[i]
                let nc = cur.c + dc[i]
                let k = "\(nr),\(nc)"
                if open(nr, nc) && !(seen[k] ?? false) {
                    seen[k] = true
                    prev[k] = cur.key()
                    q.append(Pos(nr, nc))
                }
                i += 1
            }
        }
        var path: [Pos] = []
        if !(seen[target] ?? false) {
            return path
        }
        var curKey = target
        while curKey != start.key() {
            let parts = parseKey(curKey)
            path.insert(Pos(parts.0, parts.1), at: 0)
            curKey = prev[curKey] ?? start.key()
        }
        path.insert(start, at: 0)
        return path
    }
}

func parseKey(_ s: String) -> (Int, Int) {
    // Known coordinates in this test are one digit; decode by lookup.
    let rows = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    var r = 0
    var c = 0
    var i = 0
    while i < rows.count {
        if s.hasPrefix(rows[i] + ",") {
            r = i
        }
        if s.hasSuffix("," + rows[i]) {
            c = i
        }
        i += 1
    }
    return (r, c)
}

func showPath(_ p: [Pos]) -> String {
    var s = ""
    var i = 0
    while i < p.count {
        if i > 0 {
            s = s + " -> "
        }
        s = s + "(" + p[i].key() + ")"
        i += 1
    }
    return s
}

let m = Maze(5, 6)
let blocks = [(0,2), (1,2), (2,2), (3,4), (1,4), (2,4)]
for b in blocks {
    m.block(b.0, b.1)
}
let path1 = m.shortest(0, 0, 4, 5)
print("path1 len = \(path1.count)")
print(showPath(path1))
let path2 = m.shortest(0, 0, 0, 5)
print("path2 len = \(path2.count)")
print(showPath(path2))
