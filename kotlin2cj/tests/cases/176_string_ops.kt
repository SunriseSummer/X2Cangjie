// Test: Comprehensive string operations
fun main() {
    val s = "Hello, World!"

    // Basic string operations
    println("length: ${s.length}")
    println("substring: ${s.substring(0, 5)}")
    println("indexOf: ${s.indexOf('o')}")
    println("contains: ${s.contains("World")}")
    println("startsWith: ${s.startsWith("Hello")}")
    println("endsWith: ${s.endsWith("!")}")
    println("replace: ${s.replace("World", "Cangjie")}")

    // String split and join
    val csv = "a,b,c,d,e"
    val parts = csv.split(",")
    println("split size: ${parts.size}")
    println("joined: ${parts.joinToString(" | ")}")

    // Char operations
    val digits = "abc123"
    var letterCount = 0
    var digitCount = 0
    for (c in digits) {
        if (c.isLetter()) letterCount++
        if (c.isDigit()) digitCount++
    }
    println("letters: $letterCount, digits: $digitCount")

    // String building
    val sb = StringBuilder()
    for (i in 1..5) {
        if (sb.isNotEmpty()) sb.append("-")
        sb.append(i.toString())
    }
    println("built: ${sb.toString()}")
}
