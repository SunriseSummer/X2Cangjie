import std.collection.*

class TrieNode {
    let children = HashMap<Rune, TrieNode>()
    var isEnd = false
    var count = 0
}

class Trie {
    let root = TrieNode()
    func insert(word: String) {
        var node = root
        for (c in word.runes()) {
            if (!node.children.contains(c)) {
                node.children[c] = TrieNode()
            }
            node = node.children[c]
            node.count += 1
        }
        node.isEnd = true
    }
    func search(word: String): Bool {
        var node = root
        for (c in word.runes()) {
            if (!node.children.contains(c)) {
                return false
            }
            node = node.children[c]
        }
        return node.isEnd
    }
    func startsWith(prefix: String): Bool {
        var node = root
        for (c in prefix.runes()) {
            if (!node.children.contains(c)) {
                return false
            }
            node = node.children[c]
        }
        return true
    }
    func countPrefix(prefix: String): Int64 {
        var node = root
        for (c in prefix.runes()) {
            if (!node.children.contains(c)) {
                return 0
            }
            node = node.children[c]
        }
        return node.count
    }
}

main() {
    let trie = Trie()
    let words = ArrayList(["apple", "app", "apricot", "banana", "band", "bandana"])
    for (w in words) {
        trie.insert(w)
    }
    println("search apple: ${trie.search("apple")}")
    println("search app: ${trie.search("app")}")
    println("search apt: ${trie.search("apt")}")
    println("search banana: ${trie.search("banana")}")
    println("startsWith ap: ${trie.startsWith("ap")}")
    println("startsWith ban: ${trie.startsWith("ban")}")
    println("startsWith cat: ${trie.startsWith("cat")}")
    println("count ap: ${trie.countPrefix("ap")}")
    println("count ban: ${trie.countPrefix("ban")}")
    println("count band: ${trie.countPrefix("band")}")
}
