fun main() {
    val prices = mutableMapOf("apple" to 3, "banana" to 2, "cherry" to 5)
    prices["date"] = 8
    var total = 0
    for ((name, price) in prices) {
        total += price
    }
    println("items=${prices.size} total=$total")
}
