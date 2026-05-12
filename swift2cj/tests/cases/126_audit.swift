// Large #2 (iter8): inventory audit with batches and per-location totals
class Batch {
    let id: String
    let location: String
    let sku: String
    var qty: Int
    init(_ id: String, _ location: String, _ sku: String, _ qty: Int) {
        self.id = id
        self.location = location
        self.sku = sku
        self.qty = qty
    }
}

class Audit {
    var batches: [Batch] = []
    func add(_ b: Batch) { batches.append(b) }
    func transfer(_ id: String, _ amount: Int, _ dest: String) {
        for b in batches {
            if b.id == id && b.qty >= amount {
                b.qty -= amount
                batches.append(Batch(id + ":x", dest, b.sku, amount))
                return
            }
        }
    }
    func byLocation() -> [String: Int] {
        var m: [String: Int] = [:]
        for b in batches { m[b.location] = (m[b.location] ?? 0) + b.qty }
        return m
    }
    func bySku() -> [String: Int] {
        var m: [String: Int] = [:]
        for b in batches { m[b.sku] = (m[b.sku] ?? 0) + b.qty }
        return m
    }
}

func printMap(_ title: String, _ m: [String: Int]) {
    print(title)
    var keys: [String] = []
    for (k, _) in m { keys.append(k) }
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
    for k in keys { print("  \(k)=\(m[k] ?? 0)") }
}

let audit = Audit()
audit.add(Batch("b1", "east", "tea", 30))
audit.add(Batch("b2", "west", "tea", 20))
audit.add(Batch("b3", "east", "coffee", 12))
audit.add(Batch("b4", "north", "sugar", 8))
audit.transfer("b1", 5, "west")
audit.transfer("b3", 2, "north")
printMap("location", audit.byLocation())
printMap("sku", audit.bySku())
