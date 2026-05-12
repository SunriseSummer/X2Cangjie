// Medium #1 (iter5): binary max-heap with sift up/down
class MaxHeap {
    var a: [Int] = []

    func count() -> Int {
        return a.count
    }

    func push(_ v: Int) {
        a.append(v)
        var i = a.count - 1
        while i > 0 {
            let p = (i - 1) / 2
            if a[p] < a[i] {
                let t = a[p]
                a[p] = a[i]
                a[i] = t
                i = p
            } else {
                return
            }
        }
    }

    func pop() -> Int {
        if a.count == 0 {
            return -1
        }
        let top = a[0]
        let last = a[a.count - 1]
        a.remove(at: a.count - 1)
        if a.count > 0 {
            a[0] = last
            var i = 0
            while true {
                let l = 2 * i + 1
                let r = 2 * i + 2
                var best = i
                if l < a.count && a[l] > a[best] {
                    best = l
                }
                if r < a.count && a[r] > a[best] {
                    best = r
                }
                if best == i {
                    break
                }
                let t = a[i]
                a[i] = a[best]
                a[best] = t
                i = best
            }
        }
        return top
    }

    func peek() -> Int {
        if a.count == 0 {
            return -1
        }
        return a[0]
    }
}

let h = MaxHeap()
for v in [3, 1, 9, 4, 7, 2, 8, 5, 6] {
    h.push(v)
    print("push \(v) -> top=\(h.peek())")
}
print("size = \(h.count())")
var sorted: [Int] = []
while h.count() > 0 {
    sorted.append(h.pop())
}
print("sorted desc: \(sorted)")

// Median-style usage: keep K largest.
func topK(_ xs: [Int], _ k: Int) -> [Int] {
    let hh = MaxHeap()
    for x in xs {
        hh.push(x)
    }
    var out: [Int] = []
    var i = 0
    while i < k && hh.count() > 0 {
        out.append(hh.pop())
        i += 1
    }
    return out
}
print("top3 of [4,1,7,3,9,2,5,8,6] = \(topK([4,1,7,3,9,2,5,8,6], 3))")
print("top5 = \(topK([4,1,7,3,9,2,5,8,6], 5))")
