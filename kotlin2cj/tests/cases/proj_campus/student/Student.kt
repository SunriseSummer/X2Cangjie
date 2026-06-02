class Student(val id: Int, val name: String) {
    val enrolledCourses = mutableListOf<String>()

    fun enroll(courseName: String) {
        enrolledCourses.add(courseName)
    }

    fun showInfo() {
        println("Student #$id: $name")
        if (enrolledCourses.isEmpty()) {
            println("  No courses enrolled")
        } else {
            println("  Courses: ${enrolledCourses.joinToString(", ")}")
        }
    }
}
