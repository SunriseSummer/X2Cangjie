fun main() {
    val x = 7
    if (x > 10) {
        println("big")
    } else if (x > 5) {
        println("medium")
    } else {
        println("small")
    }
    val label = if (x % 2 == 0) "even" else "odd"
    println(label)
}
