// Small #2 (iter8): temperature rolling statistics over arrays
class Stats {
    var values: [Int] = []
    func add(_ v: Int) {
        values.append(v)
    }
    func minValue() -> Int {
        var m = values[0]
        for v in values {
            if v < m { m = v }
        }
        return m
    }
    func maxValue() -> Int {
        var m = values[0]
        for v in values {
            if v > m { m = v }
        }
        return m
    }
    func averageTimes100() -> Int {
        var s = 0
        for v in values { s += v }
        return (s * 100) / values.count
    }
}
let st = Stats()
for v in [18, 21, 19, 23, 20, 17, 22] {
    st.add(v)
}
print("min=\(st.minValue()) max=\(st.maxValue()) avg100=\(st.averageTimes100())")
