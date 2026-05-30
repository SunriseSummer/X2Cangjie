fun main() {
    var n = 5
    var fact = 1
    do {
        fact *= n
        n--
    } while (n > 0)
    println("5! = $fact")
}
