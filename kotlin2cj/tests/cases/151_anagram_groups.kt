// Multimap pattern: HashMap<String, ArrayList<String>>
fun groupAnagrams(words: ArrayList<String>): ArrayList<ArrayList<String>> {
    val groups = HashMap<String, ArrayList<String>>()
    for (word in words) {
        // Sort characters to get anagram key
        val chars = ArrayList<Char>()
        for (c in word) {
            chars.add(c)
        }
        // Simple insertion sort on chars
        for (i in 1 until chars.size) {
            val key = chars[i]
            var j = i - 1
            while (j >= 0 && chars[j] > key) {
                chars[j + 1] = chars[j]
                j--
            }
            chars[j + 1] = key
        }
        val sb = StringBuilder()
        for (c in chars) {
            sb.append(c)
        }
        val sorted = sb.toString()
        if (!groups.containsKey(sorted)) {
            groups[sorted] = ArrayList<String>()
        }
        groups[sorted]!!.add(word)
    }
    val result = ArrayList<ArrayList<String>>()
    for ((_, group) in groups) {
        group.sort()
        result.add(group)
    }
    // Sort result by first element
    for (i in 0 until result.size) {
        for (j in i + 1 until result.size) {
            if (result[i][0] > result[j][0]) {
                val tmp = result[i]
                result[i] = result[j]
                result[j] = tmp
            }
        }
    }
    return result
}

fun main() {
    val words = arrayListOf("eat", "tea", "tan", "ate", "nat", "bat")
    val groups = groupAnagrams(words)
    for (group in groups) {
        println(group.joinToString(", "))
    }
}
