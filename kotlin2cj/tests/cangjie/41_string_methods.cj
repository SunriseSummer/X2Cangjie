main() {
    let raw = "  Hello World  "
    let s = raw.trimAscii()
    println("[${s}]")
    println(s.toAsciiUpper())
    println(s.toAsciiLower())
    println("len=${s.size}")
    println(s.contains("World"))
}
