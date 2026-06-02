fun main() {
    val alice = Student(1, "Alice")
    val bob = Student(2, "Bob")
    val charlie = Student(3, "Charlie")

    val math = Course("MATH101", "Mathematics", 2)
    val cs = Course("CS201", "Computer Science", 3)

    math.enrollStudent(alice)
    math.enrollStudent(bob)
    math.enrollStudent(charlie)

    cs.enrollStudent(alice)
    cs.enrollStudent(charlie)

    println()
    math.showRoster()
    println()
    cs.showRoster()

    println()
    alice.showInfo()
    bob.showInfo()
    charlie.showInfo()
}
