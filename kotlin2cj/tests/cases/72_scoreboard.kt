data class Player(val name: String, val score: Int)

fun main() {
    val players = listOf(
        Player("Alice", 88),
        Player("Bob", 72),
        Player("Carol", 95),
        Player("Dave", 60),
        Player("Eve", 81)
    )
    val total = players.sumOf { it.score }
    val avg = total / players.count()
    println("total=$total avg=$avg")
    val passed = players.filter { it.score >= 80 }
    print("passed: ")
    for (p in passed) print("${p.name} ")
    println()
    println("topScore=${players.map { it.score }.maxOrNull() ?: 0}")
    println("allPass=${players.all { it.score >= 50 }} anyPerfect=${players.any { it.score == 100 }}")
    val names = players.joinToString(", ") { it.name }
    println("roster: $names")
}
