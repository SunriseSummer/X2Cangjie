// Medium #2 (iter6): tiny CSV-style table aggregation
class Row {
    let city: String
    let product: String
    let qty: Int

    init(_ city: String, _ product: String, _ qty: Int) {
        self.city = city
        self.product = product
        self.qty = qty
    }
}

class Table {
    var rows: [Row] = []

    func add(_ city: String, _ product: String, _ qty: Int) {
        rows.append(Row(city, product, qty))
    }

    func totalByCity() -> [String: Int] {
        var m: [String: Int] = [:]
        for r in rows {
            m[r.city] = (m[r.city] ?? 0) + r.qty
        }
        return m
    }

    func totalByProduct() -> [String: Int] {
        var m: [String: Int] = [:]
        for r in rows {
            m[r.product] = (m[r.product] ?? 0) + r.qty
        }
        return m
    }

    func maxRow() -> Row? {
        if rows.count == 0 {
            return nil
        }
        var best = rows[0]
        for r in rows {
            if r.qty > best.qty {
                best = r
            }
        }
        return best
    }
}

func showMap(_ title: String, _ m: [String: Int]) {
    print(title)
    var keys: [String] = []
    for (k, _) in m {
        keys.append(k)
    }
    var i = 1
    while i < keys.count {
        var j = i
        while j > 0 && keys[j] < keys[j - 1] {
            let t = keys[j]
            keys[j] = keys[j - 1]
            keys[j - 1] = t
            j -= 1
        }
        i += 1
    }
    for k in keys {
        print("  \(k)=\(m[k] ?? 0)")
    }
}

let t = Table()
t.add("shanghai", "tea", 3)
t.add("beijing", "tea", 4)
t.add("shanghai", "coffee", 5)
t.add("shenzhen", "tea", 2)
t.add("beijing", "coffee", 7)
showMap("by city", t.totalByCity())
showMap("by product", t.totalByProduct())
let mx = t.maxRow()
if let r = mx {
    print("max row = \(r.city)/\(r.product)/\(r.qty)")
}
