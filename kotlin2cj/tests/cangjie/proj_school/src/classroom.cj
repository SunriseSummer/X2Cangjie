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
