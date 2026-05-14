// Medium #1 (iter6): disjoint-set union with component sizes
class DSU {
    var parent: [Int] = []
    var sz: [Int] = []

    init(_ n: Int) {
        var i = 0
        while i < n {
            parent.append(i)
            sz.append(1)
            i += 1
        }
    }

    func find(_ x: Int) -> Int {
        if parent[x] == x {
            return x
        }
        let r = find(parent[x])
        parent[x] = r
        return r
    }

    func unite(_ a: Int, _ b: Int) -> Bool {
        var ra = find(a)
        var rb = find(b)
        if ra == rb {
            return false
        }
        if sz[ra] < sz[rb] {
            let t = ra
            ra = rb
            rb = t
        }
        parent[rb] = ra
        sz[ra] += sz[rb]
        return true
    }

    func same(_ a: Int, _ b: Int) -> Bool {
        return find(a) == find(b)
    }

    func sizeOf(_ x: Int) -> Int {
        return sz[find(x)]
    }

    func groups(_ n: Int) -> String {
        var s = ""
        var i = 0
        while i < n {
            s = s + "\(i):\(find(i))/\(sizeOf(i)) "
            i += 1
        }
        return s
    }
}

let d = DSU(10)
let edges = [(0,1), (1,2), (3,4), (5,6), (6,7), (7,8), (2,8), (0,8), (4,9)]
for e in edges {
    let changed = d.unite(e.0, e.1)
    print("union \(e.0)-\(e.1): \(changed) -> \(d.groups(10))")
}
print("same 0 7 = \(d.same(0, 7))")
print("same 3 9 = \(d.same(3, 9))")
print("same 0 3 = \(d.same(0, 3))")
