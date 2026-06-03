func countWords(s: String): Int64 {
    let bytes = s.toArray()
    if (bytes.size == 0) {
        return 0
    }
    var count = 0
    var inWord = false
    for (i in 0..bytes.size) {
        if (bytes[i] == 32u8) {
            inWord = false
        } else if (!inWord) {
            inWord = true
            count++
        }
    }
    return count
}

main() {
    println(countWords("hello world"))
    println(countWords("one two three four"))
    println(countWords(""))
    println(countWords("single"))
    return 0
}
