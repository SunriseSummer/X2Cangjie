// Medium #2 (iter8): histogram with stable sorted output
func histogram(_ xs: [Int]) -> [Int: Int] {
    var h: [Int: Int] = [:]
    for x in xs {
        h[x] = (h[x] ?? 0) + 1
    }
    return h
}

func sortedKeys(_ m: [Int: Int]) -> [Int] {
    var keys: [Int] = []
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
    return keys
}

let xs = [4, 1, 2, 4, 3, 2, 4, 1, 5, 5, 5, 2]
let h = histogram(xs)
for k in sortedKeys(h) {
    print("\(k):\(h[k] ?? 0)")
}
