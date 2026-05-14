// Small #2: nested function used purely for scope hiding (no escaping closure)
func computeStats(_ xs: [Int]) -> (Int, Int, Int) {
    func sum(_ ys: [Int]) -> Int {
        var s = 0
        for y in ys {
            s += y
        }
        return s
    }
    func minOf(_ ys: [Int]) -> Int {
        var m = ys[0]
        for y in ys {
            if y < m { m = y }
        }
        return m
    }
    func maxOf(_ ys: [Int]) -> Int {
        var m = ys[0]
        for y in ys {
            if y > m { m = y }
        }
        return m
    }
    return (sum(xs), minOf(xs), maxOf(xs))
}

let data1 = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
let s1 = computeStats(data1)
print("sum=\(s1.0) min=\(s1.1) max=\(s1.2)")

let data2 = [-3, 10, 0, 7, -2]
let s2 = computeStats(data2)
print("sum=\(s2.0) min=\(s2.1) max=\(s2.2)")
