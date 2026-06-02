package proj_school

import std.collection.*

class Classroom {
    let roomNumber: Int64
    init(roomNumber: Int64) {
        this.roomNumber = roomNumber
    }
    let teachers = ArrayList<Teacher>()
    let allStudents = ArrayList<Student>()
    func assignTeacher(teacher: Teacher) {
        teachers.add(teacher)
        for (s in teacher.students) {
            if (!containsStudent(s.name)) {
                allStudents.add(s)
            }
        }
    }
    func containsStudent(name: String): Bool {
        for (s in allStudents) {
            if (s.name == name) {
                return true
            }
        }
        return false
    }
    func totalPeople(): Int64 {
        return teachers.size + allStudents.size
    }
    func printSummary() {
        println("Room #${roomNumber}: ${teachers.size} teachers, ${allStudents.size} students")
        for (t in teachers) {
            println("  Teacher: ${t.name} (${t.subject})")
        }
        for (s in allStudents) {
            println("  ${s.introduce()}")
        }
    }
}

open class Person {
    let name: String
    let age: Int64
    init(name: String, age: Int64) {
        this.name = name
        this.age = age
    }
    public open func role(): String {
        return "Person"
    }
    public open func introduce(): String {
        return "${role()}: ${name}, age ${age}"
    }
}

class Student <: Person {
    let grade: Int64
    init(name: String, age: Int64, grade: Int64) {
        super(name, age)
        this.grade = grade
    }
    let scores = ArrayList<Int64>()
    public override func role(): String {
        return "Student"
    }
    func addScore(score: Int64) {
        scores.add(score)
    }
    func avgScore(): Int64 {
        if (scores.isEmpty()) {
            return 0
        }
        var sum = 0
        for (s in scores) {
            sum += s
        }
        return sum / scores.size
    }
    func passed(): Bool {
        return avgScore() >= 60
    }
    func report(): String {
        return "${name} (Grade ${grade}): avg=${avgScore()}, passed=${passed()}"
    }
}

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

main() {
    let s1 = Student("Alice", 15, 9)
    s1.addScore(85)
    s1.addScore(92)
    s1.addScore(78)
    let s2 = Student("Bob", 16, 9)
    s2.addScore(45)
    s2.addScore(55)
    s2.addScore(50)
    let s3 = Student("Charlie", 15, 9)
    s3.addScore(90)
    s3.addScore(95)
    s3.addScore(88)
    let s4 = Student("Diana", 16, 9)
    s4.addScore(70)
    s4.addScore(65)
    s4.addScore(72)
    let mathTeacher = Teacher("Mr. Smith", 40, "Math")
    mathTeacher.addStudent(s1)
    mathTeacher.addStudent(s2)
    mathTeacher.addStudent(s3)
    let sciTeacher = Teacher("Ms. Jones", 35, "Science")
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
    let room = Classroom(101)
    room.assignTeacher(mathTeacher)
    room.assignTeacher(sciTeacher)
    room.printSummary()
    println("Total people in room: ${room.totalPeople()}")
}