import std.collection.*
import std.sort.*

func charFrequency(s: String): HashMap<Rune, Int64> {
    let freq = HashMap<Rune, Int64>()
    for (c in s.runes()) {
        freq[c] = (freq.get(c) ?? 0) + 1
    }
    return freq
}

func wordFrequency(s: String): HashMap<String, Int64> {
    let freq = HashMap<String, Int64>()
    let words = collectArrayList(s.split(" ").iterator())
    for (w in words) {
        freq[w] = (freq.get(w) ?? 0) + 1
    }
    return freq
}

func invertMap(map: HashMap<String, Int64>): HashMap<Int64, ArrayList<String>> {
    let result = HashMap<Int64, ArrayList<String>>()
    for ((key, value) in map) {
        if (!result.contains(value)) {
            result[value] = ArrayList<String>()
        }
        result[value].add(key)
    }
    return result
}

main() {
    let freq = charFrequency("abracadabra")
    let keys = ArrayList<String>()
    for ((k, v) in freq) {
        keys.add("${k}=${v}")
    }
    sort(keys, stable: true)
    println(String.join(collectArray<String>(keys.iterator().map({e => e.toString()})), delimiter: ", "))
    let wf = wordFrequency("the cat sat on the mat the cat")
    let wkeys = ArrayList<String>()
    for ((k, v) in wf) {
        wkeys.add("${k}:${v}")
    }
    sort(wkeys, stable: true)
    println(String.join(collectArray<String>(wkeys.iterator().map({e => e.toString()})), delimiter: ", "))
    let scores = HashMap<String, Int64>()
    scores["alice"] = 90
    scores["bob"] = 85
    scores["carol"] = 90
    scores["dave"] = 85
    let inverted = invertMap(scores)
    let invKeys = ArrayList<Int64>()
    for (k in inverted.keys()) {
        invKeys.add(k)
    }
    sort(invKeys, stable: true)
    for (score in invKeys) {
        let names = inverted[score]
        sort(names, stable: true)
        println("${score}: ${String.join(collectArray<String>(names.iterator().map({e => e.toString()})), delimiter: ", ")}")
    }
}
