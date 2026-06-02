import std.collection.*

func computeKMPTable(pattern: String): ArrayList<Int64> {
    let table = ArrayList<Int64>()
    table.add(0)
    var len = 0
    var i = 1
    while (i < pattern.size) {
        if (pattern.toRuneArray()[i] == pattern.toRuneArray()[len]) {
            len += 1
            table.add(len)
            i += 1
        } else {
            if (len != 0) {
                len = table[len - 1]
            } else {
                table.add(0)
                i += 1
            }
        }
    }
    return table
}

func kmpSearch(text: String, pattern: String): ArrayList<Int64> {
    let result = ArrayList<Int64>()
    if (pattern.isEmpty()) {
        return result
    }
    let table = computeKMPTable(pattern)
    var i = 0
    var j = 0
    while (i < text.size) {
        if (text.toRuneArray()[i] == pattern.toRuneArray()[j]) {
            i += 1
            j += 1
        }
        if (j == pattern.size) {
            result.add(i - j)
            j = table[j - 1]
        } else if ((i < text.size) && (text.toRuneArray()[i] != pattern.toRuneArray()[j])) {
            if (j != 0) {
                j = table[j - 1]
            } else {
                i += 1
            }
        }
    }
    return result
}

func countOccurrences(text: String, pattern: String): Int64 {
    return kmpSearch(text, pattern).size
}

main() {
    let positions = kmpSearch("ababcababababcab", "ababc")
    println("Found at: ${String.join(collectArray<String>(positions.iterator().map({e => e.toString()})), delimiter: " ")}")
    let pos2 = kmpSearch("aaaaaa", "aa")
    println("Found at: ${String.join(collectArray<String>(pos2.iterator().map({e => e.toString()})), delimiter: " ")}")
    let pos3 = kmpSearch("hello world", "xyz")
    println("Found at: ${String.join(collectArray<String>(pos3.iterator().map({e => e.toString()})), delimiter: " ")}")
    println("Count: ${countOccurrences("abababab", "ab")}")
    println("Count: ${countOccurrences("aaaa", "aa")}")
    let table = computeKMPTable("ababc")
    println("KMP table: ${String.join(collectArray<String>(table.iterator().map({e => e.toString()})), delimiter: " ")}")
}
