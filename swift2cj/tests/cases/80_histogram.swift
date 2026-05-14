// Small #2 (iter2): histogram / frequency counter with HashMap
let nums = [1, 2, 3, 1, 2, 1, 4, 5, 4, 1, 3, 3]
var freq: [Int: Int] = [:]
for n in nums {
    let cur = freq[n] ?? 0
    freq[n] = cur + 1
}

// Print in sorted order: iterate 1..5
var k = 1
while k <= 5 {
    let v = freq[k] ?? 0
    if v > 0 {
        print("\(k) -> \(v)")
    }
    k += 1
}

// total
var total = 0
for (_, v) in freq {
    total += v
}
print("total=\(total)")
print("kinds=\(freq.count)")
