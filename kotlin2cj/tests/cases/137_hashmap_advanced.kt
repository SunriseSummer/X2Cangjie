// HashMap advanced: frequency counting, grouping, merging
fun charFrequency(s: String): HashMap<Char, Int> {
    val freq = HashMap<Char, Int>()
    for (c in s) {
        freq[c] = (freq[c] ?: 0) + 1
    }
    return freq
}

fun wordFrequency(s: String): HashMap<String, Int> {
    val freq = HashMap<String, Int>()
    val words = s.split(" ")
    for (w in words) {
        freq[w] = (freq[w] ?: 0) + 1
    }
    return freq
}

fun invertMap(map: HashMap<String, Int>): HashMap<Int, ArrayList<String>> {
    val result = HashMap<Int, ArrayList<String>>()
    for ((key, value) in map) {
        if (!result.containsKey(value)) {
            result[value] = ArrayList<String>()
        }
        result[value]!!.add(key)
    }
    return result
}

fun main() {
    // Character frequency
    val freq = charFrequency("abracadabra")
    val keys = ArrayList<String>()
    for ((k, v) in freq) {
        keys.add("$k=$v")
    }
    keys.sort()
    println(keys.joinToString(", "))

    // Word frequency
    val wf = wordFrequency("the cat sat on the mat the cat")
    val wkeys = ArrayList<String>()
    for ((k, v) in wf) {
        wkeys.add("$k:$v")
    }
    wkeys.sort()
    println(wkeys.joinToString(", "))

    // Invert map
    val scores = HashMap<String, Int>()
    scores["alice"] = 90
    scores["bob"] = 85
    scores["carol"] = 90
    scores["dave"] = 85
    val inverted = invertMap(scores)
    val invKeys = ArrayList<Int>()
    for (k in inverted.keys) {
        invKeys.add(k)
    }
    invKeys.sort()
    for (score in invKeys) {
        val names = inverted[score]!!
        names.sort()
        println("$score: ${names.joinToString(", ")}")
    }
}
