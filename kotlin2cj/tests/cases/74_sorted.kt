fun main() {
    val grades = listOf(85, 92, 78, 64, 99, 73, 88)
    val sorted = grades.sortedDescending()
    print("ranked: ")
    for (g in sorted) print("$g ")
    println()
    println("avg=${grades.sum() / grades.size}")
}
