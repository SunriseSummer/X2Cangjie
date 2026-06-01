main() {
    let s = "Hello, World!"
    println("length=${s.size}")
    println("upper=${s.toAsciiUpper()}")
    var vowels = 0
    for (c in s.runes()) {
        if ((((((((((c == r'a') || (c == r'e')) || (c == r'i')) || (c == r'o')) || (c == r'u')) || (c == r'A')) || (c == r'E')) || (c == r'I')) || (c == r'O')) || (c == r'U')) {
            vowels += 1
        }
    }
    println("vowels=${vowels}")
    println("contains World=${s.contains("World")}")
}
