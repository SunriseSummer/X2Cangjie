// Trie data structure for prefix matching
class TrieNode {
    val children = HashMap<Char, TrieNode>()
    var isEnd = false
    var count = 0
}

class Trie {
    val root = TrieNode()

    fun insert(word: String) {
        var node = root
        for (c in word) {
            if (!node.children.containsKey(c)) {
                node.children[c] = TrieNode()
            }
            node = node.children[c]!!
            node.count++
        }
        node.isEnd = true
    }

    fun search(word: String): Boolean {
        var node = root
        for (c in word) {
            if (!node.children.containsKey(c)) {
                return false
            }
            node = node.children[c]!!
        }
        return node.isEnd
    }

    fun startsWith(prefix: String): Boolean {
        var node = root
        for (c in prefix) {
            if (!node.children.containsKey(c)) {
                return false
            }
            node = node.children[c]!!
        }
        return true
    }

    fun countPrefix(prefix: String): Int {
        var node = root
        for (c in prefix) {
            if (!node.children.containsKey(c)) {
                return 0
            }
            node = node.children[c]!!
        }
        return node.count
    }
}

fun main() {
    val trie = Trie()
    val words = arrayListOf("apple", "app", "apricot", "banana", "band", "bandana")
    for (w in words) {
        trie.insert(w)
    }

    // Search
    println("search apple: ${trie.search("apple")}")
    println("search app: ${trie.search("app")}")
    println("search apt: ${trie.search("apt")}")
    println("search banana: ${trie.search("banana")}")

    // Prefix
    println("startsWith ap: ${trie.startsWith("ap")}")
    println("startsWith ban: ${trie.startsWith("ban")}")
    println("startsWith cat: ${trie.startsWith("cat")}")

    // Count prefix
    println("count ap: ${trie.countPrefix("ap")}")
    println("count ban: ${trie.countPrefix("ban")}")
    println("count band: ${trie.countPrefix("band")}")
}
