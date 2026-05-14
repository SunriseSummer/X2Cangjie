// Small #1 (iter12): daily temperature trend analysis
func classify(_ t: Int) -> String {
    if t < 0 { return "freezing" }
    if t < 15 { return "cold" }
    if t < 28 { return "mild" }
    return "hot"
}

let temps = [-3, 4, 14, 15, 22, 31, 28]
var counts: [String: Int] = [:]
for t in temps {
    let k = classify(t)
    counts[k] = (counts[k] ?? 0) + 1
}
for k in ["freezing", "cold", "mild", "hot"] {
    print(k + "=" + "\(counts[k] ?? 0)")
}
