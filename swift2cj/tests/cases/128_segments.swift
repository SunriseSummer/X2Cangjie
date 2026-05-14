// Small #2 (iter9): compress consecutive equal integers into segments
class Segment {
    let value: Int
    let count: Int
    init(_ value: Int, _ count: Int) {
        self.value = value
        self.count = count
    }
    func show() -> String { return "\(value)x\(count)" }
}

func compress(_ xs: [Int]) -> [Segment] {
    var out: [Segment] = []
    var i = 0
    while i < xs.count {
        let v = xs[i]
        var j = i
        while j < xs.count && xs[j] == v { j += 1 }
        out.append(Segment(v, j - i))
        i = j
    }
    return out
}

let data = [1,1,1,2,2,3,1,1,4,4,4,4,2]
for s in compress(data) {
    print(s.show())
}
