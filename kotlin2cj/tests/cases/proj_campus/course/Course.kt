package course

import student.Student

class Course(val code: String, val title: String, val capacity: Int) {
    val students = mutableListOf<Student>()

    fun enrollStudent(student: Student): Boolean {
        if (students.size >= capacity) {
            println("Course $code is full!")
            return false
        }
        students.add(student)
        student.enroll(title)
        println("${student.name} enrolled in $title")
        return true
    }

    fun showRoster() {
        println("Course $code - $title (${students.size}/$capacity):")
        for (s in students) {
            println("  - ${s.name}")
        }
    }
}
