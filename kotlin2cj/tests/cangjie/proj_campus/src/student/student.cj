package proj_campus.student

import std.collection.*

public class Student {
    public let id: Int64
    public let name: String
    public init(id: Int64, name: String) {
        this.id = id
        this.name = name
    }
    public let enrolledCourses = ArrayList<String>()
    public func enroll(courseName: String) {
        enrolledCourses.add(courseName)
    }
    public func showInfo() {
        println("Student #${id}: ${name}")
        if (enrolledCourses.isEmpty()) {
            println("  No courses enrolled")
        } else {
            println("  Courses: ${String.join(collectArray<String>(enrolledCourses.iterator().map({e => e.toString()})), delimiter: ", ")}")
        }
    }
}
