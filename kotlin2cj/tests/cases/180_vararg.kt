fun sum(vararg nums: Int): Int {
    var total = 0
    for (n in nums) {
        total += n
    }
    return total
}

fun printAll(vararg messages: String) {
    for (msg in messages) {
        println(msg)
    }
}

fun main() {
    println(sum(1, 2, 3, 4, 5))
    printAll("Hello", "World", "!")
}
