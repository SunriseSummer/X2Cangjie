import std.collection.*
import std.sort.*

func groupAnagrams(words: ArrayList<String>): ArrayList<ArrayList<String>> {
    let groups = HashMap<String, ArrayList<String>>()
    for (word in words) {
        let chars = ArrayList<Rune>()
        for (c in word.runes()) {
            chars.add(c)
        }
        for (i in 1..chars.size) {
            let key = chars[i]
            var j = i - 1
            while ((j >= 0) && (chars[j] > key)) {
                chars[j + 1] = chars[j]
                j -= 1
            }
            chars[j + 1] = key
        }
        let sb = StringBuilder()
        for (c in chars) {
            sb.append(c)
        }
        let sorted = sb.toString()
        if (!groups.contains(sorted)) {
            groups[sorted] = ArrayList<String>()
        }
        groups[sorted].add(word)
    }
    let result = ArrayList<ArrayList<String>>()
    for ((_, group) in groups) {
        sort(group, stable: true)
        result.add(group)
    }
    for (i in 0..result.size) {
        for (j in (i + 1)..result.size) {
            if (result[i][0] > result[j][0]) {
                let tmp = result[i]
                result[i] = result[j]
                result[j] = tmp
            }
        }
    }
    return result
}

main() {
    let words = ArrayList(["eat", "tea", "tan", "ate", "nat", "bat"])
    let groups = groupAnagrams(words)
    for (group in groups) {
        println(String.join(collectArray<String>(group.iterator().map({e => e.toString()})), delimiter: ", "))
    }
}
