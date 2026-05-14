// Small #2 (iter5): sliding window max k
func maxInWindow(_ a: [Int], _ k: Int) -> [Int] {
    var out: [Int] = []
    if a.count < k || k <= 0 {
        return out
    }
    var i = 0
    while i + k <= a.count {
        var m = a[i]
        var j = 1
        while j < k {
            if a[i + j] > m {
                m = a[i + j]
            }
            j += 1
        }
        out.append(m)
        i += 1
    }
    return out
}

let xs = [4, 1, 7, 3, 9, 2, 5, 8, 6]
print("k=1: \(maxInWindow(xs, 1))")
print("k=2: \(maxInWindow(xs, 2))")
print("k=3: \(maxInWindow(xs, 3))")
print("k=4: \(maxInWindow(xs, 4))")
print("k=9: \(maxInWindow(xs, 9))")

let ys = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
print("desc k=3: \(maxInWindow(ys, 3))")

let zs = [1, 1, 1, 1, 1]
print("flat k=2: \(maxInWindow(zs, 2))")
