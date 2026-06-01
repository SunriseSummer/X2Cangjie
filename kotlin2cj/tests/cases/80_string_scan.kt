fun main() {
    val s = "Hello, World!"
    println("length=${s.length}")
    println("upper=${s.uppercase()}")
    var vowels = 0
    for (c in s) {
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
            c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U') vowels += 1
    }
    println("vowels=$vowels")
    println("contains World=${s.contains("World")}")
}
