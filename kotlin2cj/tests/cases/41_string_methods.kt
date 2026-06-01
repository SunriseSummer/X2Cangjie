fun main() {
    val raw = "  Hello World  "
    val s = raw.trim()
    println("[${s}]")
    println(s.toUpperCase())
    println(s.toLowerCase())
    println("len=${s.length}")
    println(s.contains("World"))
}
