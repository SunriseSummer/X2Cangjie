class Classroom(val roomNumber: Int) {
    val teachers = mutableListOf<Teacher>()
    val allStudents = mutableListOf<Student>()

    fun assignTeacher(teacher: Teacher) {
        teachers.add(teacher)
        for (s in teacher.students) {
            if (!containsStudent(s.name)) {
                allStudents.add(s)
            }
        }
    }

    fun containsStudent(name: String): Boolean {
        for (s in allStudents) {
            if (s.name == name) return true
        }
        return false
    }

    fun totalPeople(): Int = teachers.size + allStudents.size

    fun printSummary() {
        println("Room #$roomNumber: ${teachers.size} teachers, ${allStudents.size} students")
        for (t in teachers) {
            println("  Teacher: ${t.name} (${t.subject})")
        }
        for (s in allStudents) {
            println("  ${s.introduce()}")
        }
    }
}
