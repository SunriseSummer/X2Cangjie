import std.collection.*

func getPair(): (String, Int64) {
    return ("Alice", 30)
}

func getTriple(): (String, Int64, Bool) {
    return ("Bob", 25, true)
}

main() {
    let (name, age) = getPair()
    println("${name} is ${age} years old")
    let (name2, age2, active) = getTriple()
    println("${name2} is ${age2}, active=${active}")
    let people = ArrayList([("Charlie", 35), ("Diana", 28), ("Eve", 42)])
    for ((n, a) in people) {
        println("${n}: ${a}")
    }
    var (x, y) = (10, 20)
    println("Before: x=${x}, y=${y}")
    x = x + 1
    y = y * 2
    println("After: x=${x}, y=${y}")
}
