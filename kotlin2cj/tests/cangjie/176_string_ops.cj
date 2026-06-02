import std.collection.*

main() {
    let s = "Hello, World!"
    println("length: ${s.size}")
    println("substring: ${s[0..5]}")
    println("indexOf: ${(s.indexOf("o") ?? -1)}")
    println("contains: ${s.contains("World")}")
    println("startsWith: ${s.startsWith("Hello")}")
    println("endsWith: ${s.endsWith("!")}")
    println("replace: ${s.replace("World", "Cangjie")}")
    let csv = "a,b,c,d,e"
    let parts = collectArrayList(csv.split(",").iterator())
    println("split size: ${parts.size}")
    println("joined: ${String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " | ")}")
    let digits = "abc123"
    var letterCount = 0
    var digitCount = 0
    for (c in digits.runes()) {
        if (c.isAsciiLetter()) {
            letterCount += 1
        }
        if (c.isAsciiNumber()) {
            digitCount += 1
        }
    }
    println("letters: ${letterCount}, digits: ${digitCount}")
    let sb = StringBuilder()
    for (i in 1..=5) {
        if ((sb.toString().size > 0)) {
            sb.append("-")
        }
        sb.append(i.toString())
    }
    println("built: ${sb.toString()}")
}
