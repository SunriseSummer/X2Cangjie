class Teacher(name: String, age: Int, val subject: String) : Person(name, age) {
    val students = mutableListOf<Student>()

    override fun role(): String = "Teacher"

    fun addStudent(student: Student) {
        students.add(student)
    }

    fun topStudent(): Student? {
        if (students.isEmpty()) return null
        var best = students[0]
        for (i in 1 until students.size) {
            if (students[i].avgScore() > best.avgScore()) {
                best = students[i]
            }
        }
        return best
    }

    fun classAverage(): Int {
        if (students.isEmpty()) return 0
        var sum = 0
        for (i in 0 until students.size) {
            sum += students[i].avgScore()
        }
        return sum / students.size
    }

    fun passRate(): Int {
        if (students.isEmpty()) return 0
        var passed = 0
        for (s in students) {
            if (s.passed()) {
                passed++
            }
        }
        return passed * 100 / students.size
    }

    fun printClassReport() {
        println("=== ${subject} Class Report (${name}) ===")
        for (s in students) {
            println("  ${s.report()}")
        }
        println("  Class average: ${classAverage()}")
        println("  Pass rate: ${passRate()}%")
        val top = topStudent()
        if (top != null) {
            println("  Top student: ${top.name}")
        }
    }
}
