// Small #1 (iter2): word and prefix checks
func countContains(_ words: [String], _ needle: String) -> Int {
    var n = 0
    for w in words {
        if w.contains(needle) {
            n += 1
        }
    }
    return n
}

func longest(_ words: [String]) -> String {
    var best = ""
    for w in words {
        if w.count > best.count {
            best = w
        }
    }
    return best
}

let words = ["hello", "swift", "cangjie", "world", "swiftui", "core"]
print("has 'sw' = \(countContains(words, "sw"))")
print("has 'o' = \(countContains(words, "o"))")
print("has 'zz' = \(countContains(words, "zz"))")
print("longest = \(longest(words))")
print("total chars = \(words[0].count + words[1].count + words[2].count + words[3].count + words[4].count + words[5].count)")
