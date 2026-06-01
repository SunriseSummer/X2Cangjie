fun main() {
    val nums = listOf(3, 1, 4, 1, 5, 9, 2, 6)
    for (x in nums.filter { it % 2 == 0 }.map { it * it }) {
        print("$x ")
    }
    println()
    val s = nums.filter { it > 2 }.sum()
    println("sum=$s")
    println("any=${nums.any { it > 8 }} all=${nums.all { it > 0 }} none=${nums.none { it > 100 }}")
    println("evens=${nums.count { it % 2 == 0 }}")
    val words = listOf("apple", "fig", "cherry")
    println("totlen=${words.sumOf { it.length }}")
    val folded = nums.fold(100) { acc, n -> acc + n }
    println("folded=$folded")
    println("reduced=${nums.reduce { a, b -> a + b }}")
    println("max=${nums.maxOrNull() ?: 0} min=${nums.minOrNull() ?: 0}")
    println(words.joinToString(", ") { it.uppercase() })
}
