fun main() {
    val s1 = Student("Alice", 15, 9)
    s1.addScore(85)
    s1.addScore(92)
    s1.addScore(78)

    val s2 = Student("Bob", 16, 9)
    s2.addScore(45)
    s2.addScore(55)
    s2.addScore(50)

    val s3 = Student("Charlie", 15, 9)
    s3.addScore(90)
    s3.addScore(95)
    s3.addScore(88)

    val s4 = Student("Diana", 16, 9)
    s4.addScore(70)
    s4.addScore(65)
    s4.addScore(72)

    val mathTeacher = Teacher("Mr. Smith", 40, "Math")
    mathTeacher.addStudent(s1)
    mathTeacher.addStudent(s2)
    mathTeacher.addStudent(s3)

    val sciTeacher = Teacher("Ms. Jones", 35, "Science")
    sciTeacher.addStudent(s1)
    sciTeacher.addStudent(s3)
    sciTeacher.addStudent(s4)

    println(mathTeacher.introduce())
    println(sciTeacher.introduce())
    println()

    mathTeacher.printClassReport()
    println()
    sciTeacher.printClassReport()

    println()
    val room = Classroom(101)
    room.assignTeacher(mathTeacher)
    room.assignTeacher(sciTeacher)
    room.printSummary()
    println("Total people in room: ${room.totalPeople()}")
}
