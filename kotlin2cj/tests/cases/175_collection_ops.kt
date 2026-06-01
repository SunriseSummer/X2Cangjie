// Test: Richer collection operations (filter, map, fold, reduce, sorted)
fun main() {
    val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

    // filter + map chain
    val evenDoubled = numbers.filter { it % 2 == 0 }.map { it * 2 }
    println("evenDoubled: ${evenDoubled.joinToString(", ")}")

    // take/drop
    val first3 = numbers.take(3)
    val rest = numbers.drop(3)
    println("first3: ${first3.joinToString(", ")}")
    println("rest: ${rest.joinToString(", ")}")

    // any/all
    println("any > 5: ${numbers.any { it > 5 }}")
    println("all > 0: ${numbers.all { it > 0 }}")

    // fold and reduce
    val sum = numbers.fold(0) { acc, x -> acc + x }
    println("fold sum: $sum")

    val product = numbers.take(5).reduce { acc, x -> acc * x }
    println("reduce product(1..5): $product")

    // sorted variants
    val unsorted = listOf(5, 3, 1, 4, 2)
    println("sorted: ${unsorted.sorted().joinToString(", ")}")
    println("sortedDescending: ${unsorted.sortedDescending().joinToString(", ")}")
}
