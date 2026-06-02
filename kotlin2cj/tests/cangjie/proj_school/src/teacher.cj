package proj_school

import std.collection.*

class Teacher <: Person {
    let subject: String
    init(name: String, age: Int64, subject: String) {
        super(name, age)
        this.subject = subject
    }
    let students = ArrayList<Student>()
    public override func role(): String {
        return "Teacher"
    }
    func addStudent(student: Student) {
        students.add(student)
    }
    func topStudent(): ?Student {
        if (students.isEmpty()) {
            return None
        }
        var best = students[0]
        for (i in 1..students.size) {
            if (students[i].avgScore() > best.avgScore()) {
                best = students[i]
            }
        }
        return best
    }
    func classAverage(): Int64 {
        if (students.isEmpty()) {
            return 0
        }
        var sum = 0
        for (i in 0..students.size) {
            sum += students[i].avgScore()
        }
        return sum / students.size
    }
    func passRate(): Int64 {
        if (students.isEmpty()) {
            return 0
        }
        var passed = 0
        for (s in students) {
            if (s.passed()) {
                passed += 1
            }
        }
        return (passed * 100) / students.size
    }
    func printClassReport() {
        println("=== ${subject} Class Report (${name}) ===")
        for (s in students) {
            println("  ${s.report()}")
        }
        println("  Class average: ${classAverage()}")
        println("  Pass rate: ${passRate()}%")
        let top = topStudent()
        if (let Some(top) <- top) {
            println("  Top student: ${top.name}")
        }
    }
}
