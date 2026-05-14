// Small #2 (iter12): sliding window maximum sum
func maxWindowSum(_ xs: [Int], _ width: Int) -> Int {
    if xs.count == 0 || width <= 0 || width > xs.count { return 0 }
    var cur = 0
    var i = 0
    while i < width { cur += xs[i]; i += 1 }
    var best = cur
    while i < xs.count {
        cur += xs[i]
        cur -= xs[i - width]
        best = max(best, cur)
        i += 1
    }
    return best
}

print(maxWindowSum([2, -1, 5, 3, -2, 4], 3))
print(maxWindowSum([1, 2], 4))
