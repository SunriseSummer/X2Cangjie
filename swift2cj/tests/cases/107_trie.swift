// Large #1 (iter5): trie-based autocomplete keyed by 1-char Strings (~250 lines).
//
// Uses a small ASCII alphabet probe to enumerate characters without per-Rune
// APIs.  Each node maps single-char-string → child, so the dictionary key
// type is plain ``String`` and translates cleanly.

let ALPHA = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o",
             "p","q","r","s","t","u","v","w","x","y","z"]

func lead(_ s: String) -> String {
    var i = 0
    while i < ALPHA.count {
        if s.hasPrefix(ALPHA[i]) {
            return ALPHA[i]
        }
        i += 1
    }
    return ""
}

func rest(_ s: String) -> String {
    let l = lead(s)
    if l == "" {
        return s
    }
    // Greedy reconstruction of the suffix by repeatedly probing alpha.
    var out = ""
    var i = 0
    while i < ALPHA.count {
        if s.hasPrefix(l + out + ALPHA[i]) {
            out = out + ALPHA[i]
            i = 0
            continue
        }
        i += 1
    }
    return out
}

class TrieNode {
    var children: [String: TrieNode] = [:]
    var isWord: Bool = false
    var count: Int = 0
}

class Trie {
    var root: TrieNode = TrieNode()

    func insert(_ w: String) {
        var node = root
        var r = w
        while r.count > 0 {
            let c = lead(r)
            if c == "" {
                break
            }
            let nxt: TrieNode
            if let n = node.children[c] {
                nxt = n
            } else {
                let n = TrieNode()
                node.children[c] = n
                nxt = n
            }
            node = nxt
            r = rest(r)
        }
        node.isWord = true
        node.count += 1
    }

    func find(_ w: String) -> TrieNode? {
        var node = root
        var r = w
        while r.count > 0 {
            let c = lead(r)
            if c == "" {
                return nil
            }
            if let n = node.children[c] {
                node = n
            } else {
                return nil
            }
            r = rest(r)
        }
        return node
    }

    func contains(_ w: String) -> Bool {
        let n = find(w)
        if let nn = n {
            return nn.isWord
        }
        return false
    }

    func countOf(_ w: String) -> Int {
        let n = find(w)
        if let nn = n {
            return nn.count
        }
        return 0
    }

    func collect(_ node: TrieNode, _ prefix: String, _ out: inout [String]) {
        if node.isWord {
            out.append(prefix)
        }
        // Deterministic order: walk ALPHA in fixed sequence.
        var i = 0
        while i < ALPHA.count {
            let k = ALPHA[i]
            if let c = node.children[k] {
                collect(c, prefix + k, &out)
            }
            i += 1
        }
    }

    func autocomplete(_ prefix: String) -> [String] {
        var out: [String] = []
        let n = find(prefix)
        if let nn = n {
            collect(nn, prefix, &out)
        }
        return out
    }
}

let t = Trie()
let words = ["car", "card", "care", "careful", "cart", "cat", "category", "cargo", "carbon", "bat", "bar", "barn", "band"]
for w in words {
    t.insert(w)
}
t.insert("car")
t.insert("car")
t.insert("cat")

print("contains car = \(t.contains("car"))")
print("contains carp = \(t.contains("carp"))")
print("count(car) = \(t.countOf("car"))")
print("count(cat) = \(t.countOf("cat"))")
print("count(careful) = \(t.countOf("careful"))")

print("auto(ca) = \(t.autocomplete("ca"))")
print("auto(car) = \(t.autocomplete("car"))")
print("auto(ba) = \(t.autocomplete("ba"))")
print("auto(z) = \(t.autocomplete("z"))")

