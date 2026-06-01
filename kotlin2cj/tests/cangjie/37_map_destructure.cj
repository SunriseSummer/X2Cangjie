import std.collection.*

main() {
    let prices = HashMap([("apple", 3), ("banana", 2), ("cherry", 5)])
    prices["date"] = 8
    var total = 0
    for ((name, price) in prices) {
        total += price
    }
    println("items=${prices.size} total=${total}")
}
