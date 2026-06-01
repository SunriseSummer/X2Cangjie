data class Student(val name: String, val score: Int)

fun grade(score: Int): String = when {
    score >= 90 -> "A"
    score >= 80 -> "B"
    score >= 70 -> "C"
    else -> "F"
}

fun main() {
    val students = listOf(
        Student("amy", 95),
        Student("ben", 82),
        Student("cara", 73),
        Student("dan", 60)
    )
    var total = 0
    for (s in students) {
        total = total + s.score
        println("${s.name}: ${grade(s.score)}")
    }
    val avg = total / students.size
    println("avg=$avg grade=${grade(avg)}")
}
