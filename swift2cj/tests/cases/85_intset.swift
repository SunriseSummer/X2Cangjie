// Small #1 (iter3): naïve "Set" implemented via [Int] dedup
class IntSet {
    var items: [Int] = []
    func add(_ v: Int) -> Bool {
        for x in items {
            if x == v {
                return false
            }
        }
        items.append(v)
        return true
    }
    func contains(_ v: Int) -> Bool {
        for x in items {
            if x == v {
                return true
            }
        }
        return false
    }
    func size() -> Int {
        return items.count
    }
}

let s = IntSet()
let arr = [1, 2, 1, 3, 2, 5, 4, 3, 4, 6]
var added = 0
for v in arr {
    if s.add(v) {
        added += 1
    }
}
print("size=\(s.size()) added=\(added)")
print("has 3 = \(s.contains(3))")
print("has 99 = \(s.contains(99))")

// intersection
let s2 = IntSet()
for v in [2, 4, 6, 8, 10] {
    let _ = s2.add(v)
}
var inter = 0
for v in s.items {
    if s2.contains(v) {
        inter += 1
    }
}
print("intersection size = \(inter)")
