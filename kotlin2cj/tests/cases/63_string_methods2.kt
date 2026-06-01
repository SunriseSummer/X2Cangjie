fun main() {
    val s = "hello,world,foo"
    println(s.substring(0, 5))
    println(s.substring(6))
    val parts = s.split(",")
    println(parts.size)
    println(parts.first())
    println(parts.last())
    println(parts.isNotEmpty())
    println(parts.joinToString(" | "))
    println(s.replace(",", "-"))
    println(s.contains("world"))
    println(s.startsWith("hello"))
}
