// Small #2 (iter11): greedy text wrapping
func wrap(_ words: [String], _ width: Int) -> [String] {
    var lines: [String] = []
    var current = ""
    for w in words {
        if current.count == 0 {
            current = w
        } else if current.count + 1 + w.count <= width {
            current = current + " " + w
        } else {
            lines.append(current)
            current = w
        }
    }
    if current.count > 0 { lines.append(current) }
    return lines
}

let words = ["swift", "to", "cangjie", "translation", "needs", "semantic", "checks"]
let lines = wrap(words, 16)
var i = 0
for line in lines {
    print("\(i):" + line + ":\(line.count)")
    i += 1
}
