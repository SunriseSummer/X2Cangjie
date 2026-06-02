import std.collection.*

main() {
    let words = ArrayList(["apple", "banana", "apple", "cherry", "banana", "apple"])
    let freq = HashMap<String, Int64>()
    for (w in words) {
        freq[w] = (freq.get(w) ?? 0) + 1
    }
    let sorted = ArrayList(["apple", "banana", "cherry"])
    for (k in sorted) {
        println("${k}: ${freq[k]}")
    }
    let matrix = ArrayList([ArrayList([1, 2, 3]), ArrayList([4, 5, 6]), ArrayList([7, 8, 9])])
    let sb = StringBuilder()
    for (row in matrix) {
        for (i in 0..=(row.size - 1)) {
            if (i > 0) {
                sb.append(" ")
            }
            sb.append(row[i])
        }
        sb.append("\n")
    }
    print(sb.toString())
    var result = ""
    for (i in 1..=5) {
        result += i.toString()
        if (i < 5) {
            result += "-"
        }
    }
    println(result)
}
