class Student(val name: String, val score: Int) {
    fun grade(): String {
        return when {
            score >= 90 -> "A"
            score >= 80 -> "B"
            score >= 70 -> "C"
            else -> "F"
        }
    }
}
fun average(students: MutableList<Student>): Int {
    var sum = 0
    for (s in students) {
        sum += s.score
    }
    return sum / students.size
}
fun main() {
    val students = mutableListOf(
        Student("alice", 92),
        Student("bob", 78),
        Student("carol", 85),
        Student("dave", 60)
    )
    for (s in students) {
        println("${s.name}: ${s.score} (${s.grade()})")
    }
    println("average=${average(students)}")
}
