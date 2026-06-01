fun gradePoint(letter: String): Int {
    return when (letter) {
        "A" -> 4
        "B" -> 3
        "C", "D" -> 2
        else -> 0
    }
}
fun main() {
    val grades = listOf("A", "B", "C", "D", "F")
    var sum = 0
    for (g in grades) {
        sum += gradePoint(g)
    }
    println("sum=$sum")
    for (g in grades) {
        println("$g -> ${gradePoint(g)}")
    }
}
