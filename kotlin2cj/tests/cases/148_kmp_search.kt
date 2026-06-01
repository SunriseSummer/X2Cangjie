// String pattern matching: KMP algorithm
fun computeKMPTable(pattern: String): ArrayList<Int> {
    val table = ArrayList<Int>()
    table.add(0)
    var len = 0
    var i = 1
    while (i < pattern.length) {
        if (pattern[i] == pattern[len]) {
            len++
            table.add(len)
            i++
        } else {
            if (len != 0) {
                len = table[len - 1]
            } else {
                table.add(0)
                i++
            }
        }
    }
    return table
}

fun kmpSearch(text: String, pattern: String): ArrayList<Int> {
    val result = ArrayList<Int>()
    if (pattern.isEmpty()) return result

    val table = computeKMPTable(pattern)
    var i = 0
    var j = 0
    while (i < text.length) {
        if (text[i] == pattern[j]) {
            i++
            j++
        }
        if (j == pattern.length) {
            result.add(i - j)
            j = table[j - 1]
        } else if (i < text.length && text[i] != pattern[j]) {
            if (j != 0) {
                j = table[j - 1]
            } else {
                i++
            }
        }
    }
    return result
}

fun countOccurrences(text: String, pattern: String): Int {
    return kmpSearch(text, pattern).size
}

fun main() {
    // KMP search
    val positions = kmpSearch("ababcababababcab", "ababc")
    println("Found at: ${positions.joinToString(" ")}")

    // Multiple occurrences
    val pos2 = kmpSearch("aaaaaa", "aa")
    println("Found at: ${pos2.joinToString(" ")}")

    // No match
    val pos3 = kmpSearch("hello world", "xyz")
    println("Found at: ${pos3.joinToString(" ")}")

    // Count occurrences
    println("Count: ${countOccurrences("abababab", "ab")}")
    println("Count: ${countOccurrences("aaaa", "aa")}")

    // KMP table for pattern
    val table = computeKMPTable("ababc")
    println("KMP table: ${table.joinToString(" ")}")
}
