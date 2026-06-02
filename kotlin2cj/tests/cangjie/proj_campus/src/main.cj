package proj_campus

import std.collection.*
import proj_campus.course.*
import proj_campus.student.*

main() {
    let alice = Student(1, "Alice")
    let bob = Student(2, "Bob")
    let charlie = Student(3, "Charlie")
    let math = Course("MATH101", "Mathematics", 2)
    let cs = Course("CS201", "Computer Science", 3)
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
