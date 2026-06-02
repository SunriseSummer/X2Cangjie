func buildTable(rows: Int64, cols: Int64): String {
    let sb = StringBuilder()
    for (i in 1..=rows) {
        for (j in 1..=cols) {
            let v = i * j
            if (v < 10) {
                sb.append(" ")
            }
            sb.append(v)
            if (j < cols) {
                sb.append(" ")
            }
        }
        sb.append("\n")
    }
    return sb.toString()
}

func repeatChar(c: Rune, n: Int64): String {
    let sb = StringBuilder()
    for (i in 0..n) {
        sb.append(c)
    }
    return sb.toString()
}

func buildPyramid(height: Int64): String {
    let sb = StringBuilder()
    for (i in 1..=height) {
        sb.append(repeatChar(r' ', height - i))
        sb.append(repeatChar(r'*', (2 * i) - 1))
        sb.append("\n")
    }
    return sb.toString()
}

func interleave(a: String, b: String): String {
    let sb = StringBuilder()
    let maxLen = if (a.size > b.size) {
        a.size
    } else {
        b.size
    }
    for (i in 0..maxLen) {
        if (i < a.size) {
            sb.append(a.toRuneArray()[i])
        }
        if (i < b.size) {
            sb.append(b.toRuneArray()[i])
        }
    }
    return sb.toString()
}

main() {
    print(buildTable(3, 4))
    print(buildPyramid(4))
    println(interleave("abc", "12345"))
    println(interleave("hello", "xy"))
    let sb = StringBuilder()
    for (i in 1..=5) {
        sb.append(i)
        if (i < 5) {
            sb.append("-")
        }
    }
    println(sb.toString())
}
