package proj_campus.course

import std.collection.*
import proj_campus.student.*

public class Course {
    public let code: String
    public let title: String
    public let capacity: Int64
    public init(code: String, title: String, capacity: Int64) {
        this.code = code
        this.title = title
        this.capacity = capacity
    }
    public let students = ArrayList<Student>()
    public func enrollStudent(student: Student): Bool {
        if (students.size >= capacity) {
            println("Course ${code} is full!")
            return false
        }
        students.add(student)
        student.enroll(title)
        println("${student.name} enrolled in ${title}")
        return true
    }
    public func showRoster() {
        println("Course ${code} - ${title} (${students.size}/${capacity}):")
        for (s in students) {
            println("  - ${s.name}")
        }
    }
}
