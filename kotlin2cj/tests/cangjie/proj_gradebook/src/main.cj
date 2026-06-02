package proj_gradebook

import std.collection.*

main() {
    let book = GradeBook()
    book.addStudent("Alice", 1)
    book.addStudent("Bob", 2)
    book.addStudent("Carol", 3)
    book.addGrade(1, 95)
    book.addGrade(1, 88)
    book.addGrade(1, 92)
    book.addGrade(2, 72)
    book.addGrade(2, 65)
    book.addGrade(2, 78)
    book.addGrade(3, 55)
    book.addGrade(3, 60)
    book.addGrade(3, 48)
    println("=== Grade Report ===")
    book.printReport()
    println("\nClass size: ${book.students.size}")
}
