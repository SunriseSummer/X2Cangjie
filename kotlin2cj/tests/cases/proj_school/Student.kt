class Student(name: String, age: Int, val grade: Int) : Person(name, age) {
    val scores = mutableListOf<Int>()

    override fun role(): String = "Student"

    fun addScore(score: Int) {
        scores.add(score)
    }

    fun avgScore(): Int {
        if (scores.isEmpty()) return 0
        var sum = 0
        for (s in scores) {
            sum += s
        }
        return sum / scores.size
    }

    fun passed(): Boolean = avgScore() >= 60

    fun report(): String {
        return "$name (Grade $grade): avg=${avgScore()}, passed=${passed()}"
    }
}
