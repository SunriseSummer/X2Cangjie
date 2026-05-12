// Small #1 (iter7): merge overlapping intervals
class Interval {
    var start: Int
    var end: Int
    init(_ start: Int, _ end: Int) {
        self.start = start
        self.end = end
    }
    func show() -> String {
        return "[\(start),\(end)]"
    }
}

func mergeIntervals(_ xs: [Interval]) -> [Interval] {
    var sorted: [Interval] = []
    for x in xs {
        var i = 0
        while i < sorted.count && sorted[i].start < x.start {
            i += 1
        }
        sorted.insert(x, at: i)
    }
    var out: [Interval] = []
    for x in sorted {
        if out.count == 0 {
            out.append(Interval(x.start, x.end))
        } else {
            let last = out[out.count - 1]
            if x.start <= last.end {
                if x.end > last.end {
                    last.end = x.end
                }
            } else {
                out.append(Interval(x.start, x.end))
            }
        }
    }
    return out
}

let data = [Interval(5, 8), Interval(1, 3), Interval(2, 6), Interval(10, 12), Interval(11, 15), Interval(20, 21)]
let merged = mergeIntervals(data)
for m in merged {
    print(m.show())
}
