// Test: Enhanced destructuring declarations
fun getPair(): Pair<String, Int> = Pair("Alice", 30)
fun getTriple(): Triple<String, Int, Boolean> = Triple("Bob", 25, true)

fun main() {
    // Pair destructuring
    val (name, age) = getPair()
    println("$name is $age years old")

    // Triple destructuring
    val (name2, age2, active) = getTriple()
    println("$name2 is $age2, active=$active")

    // Destructuring in for loop with list of pairs
    val people = listOf(Pair("Charlie", 35), Pair("Diana", 28), Pair("Eve", 42))
    for ((n, a) in people) {
        println("$n: $a")
    }

    // Destructuring with mutable
    var (x, y) = Pair(10, 20)
    println("Before: x=$x, y=$y")
    x = x + 1
    y = y * 2
    println("After: x=$x, y=$y")
}
