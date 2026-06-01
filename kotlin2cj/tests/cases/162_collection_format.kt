// Test: Chained ArrayList/Map operations & complex string formatting
fun main() {
    // Frequency counter
    val words = arrayListOf("apple", "banana", "apple", "cherry", "banana", "apple")
    val freq = HashMap<String, Int>()
    for (w in words) {
        freq[w] = (freq.getOrDefault(w, 0)) + 1
    }
    val sorted = arrayListOf("apple", "banana", "cherry")
    for (k in sorted) {
        println("$k: ${freq[k]}")
    }

    // Matrix string formatting
    val matrix = arrayListOf(
        arrayListOf(1, 2, 3),
        arrayListOf(4, 5, 6),
        arrayListOf(7, 8, 9)
    )
    val sb = StringBuilder()
    for (row in matrix) {
        for (i in 0..row.size - 1) {
            if (i > 0) sb.append(" ")
            sb.append(row[i])
        }
        sb.append("\n")
    }
    print(sb.toString())

    // Accumulative concat
    var result = ""
    for (i in 1..5) {
        result += i.toString()
        if (i < 5) result += "-"
    }
    println(result)
}
