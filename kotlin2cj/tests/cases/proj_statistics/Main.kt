fun main() {
    val numbers = mutableListOf(4, 2, 7, 2, 9, 4, 4, 1, 6, 8)
    val stats = Statistics(numbers)

    println("Data: $numbers")
    println("Mean: ${stats.mean()}")
    println("Median: ${stats.median()}")
    println("Mode: ${stats.mode()}")
    println("Variance: ${stats.variance()}")
    println("Max: ${stats.max()}")
    println("Min: ${stats.min()}")
    println("Range: ${stats.range()}")
}
