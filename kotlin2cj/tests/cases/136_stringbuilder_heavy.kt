// Heavy StringBuilder usage: building complex strings
fun buildTable(rows: Int, cols: Int): String {
    val sb = StringBuilder()
    for (i in 1..rows) {
        for (j in 1..cols) {
            val v = i * j
            if (v < 10) sb.append(" ")
            sb.append(v)
            if (j < cols) sb.append(" ")
        }
        sb.append("\n")
    }
    return sb.toString()
}

fun repeatChar(c: Char, n: Int): String {
    val sb = StringBuilder()
    for (i in 0 until n) {
        sb.append(c)
    }
    return sb.toString()
}

fun buildPyramid(height: Int): String {
    val sb = StringBuilder()
    for (i in 1..height) {
        sb.append(repeatChar(' ', height - i))
        sb.append(repeatChar('*', 2 * i - 1))
        sb.append("\n")
    }
    return sb.toString()
}

fun interleave(a: String, b: String): String {
    val sb = StringBuilder()
    val maxLen = if (a.length > b.length) a.length else b.length
    for (i in 0 until maxLen) {
        if (i < a.length) sb.append(a[i])
        if (i < b.length) sb.append(b[i])
    }
    return sb.toString()
}

fun main() {
    // Multiplication table 3x4
    print(buildTable(3, 4))

    // Pyramid
    print(buildPyramid(4))

    // Interleave
    println(interleave("abc", "12345"))
    println(interleave("hello", "xy"))

    // Chain of appends
    val sb = StringBuilder()
    for (i in 1..5) {
        sb.append(i)
        if (i < 5) sb.append("-")
    }
    println(sb.toString())
}
