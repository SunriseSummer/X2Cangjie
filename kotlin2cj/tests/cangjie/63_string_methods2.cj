import std.collection.*

main() {
    let s = "hello,world,foo"
    println(s[0..5])
    println(s[6..])
    let parts = collectArrayList(s.split(",").iterator())
    println(parts.size)
    println(parts[0])
    println(parts[parts.size - 1])
    println(!(parts.isEmpty()))
    println(String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " | "))
    println(s.replace(",", "-"))
    println(s.contains("world"))
    println(s.startsWith("hello"))
}
