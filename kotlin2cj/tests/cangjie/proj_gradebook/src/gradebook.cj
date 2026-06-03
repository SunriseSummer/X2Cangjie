package proj_gradebook

import std.collection.*

class Student <: ToString {
    let name: String
    let id: Int64
    init(name: String, id: Int64) {
        this.name = name
        this.id = id
    }
    public func toString(): String {
        return "Student(name=${this.name}, id=${this.id})"
    }
}

class GradeBook {
    let students = ArrayList<Student>()
    let grades = HashMap<Int64, ArrayList<Int64>>()
    func addStudent(name: String, id: Int64) {
        students.add(Student(name, id))
        grades[id] = ArrayList<Int64>()
    }
    func addGrade(studentId: Int64, grade: Int64) {
        grades[studentId].add(grade)
    }
    func getAverage(studentId: Int64): Int64 {
        let list = grades[studentId]
        if (list.isEmpty()) {
            return 0
        }
        var sum = 0
        for (g in list) {
            sum += g
        }
        return sum / list.size
    }
    func getHighest(studentId: Int64): Int64 {
        let list = grades[studentId]
        if (list.isEmpty()) {
            return 0
        }
        var max = list[0]
        for (g in list) {
            if (g > max) {
                max = g
            }
        }
        return max
    }
    func getLowest(studentId: Int64): Int64 {
        let list = grades[studentId]
        if (list.isEmpty()) {
            return 0
        }
        var min = list[0]
        for (g in list) {
            if (g < min) {
                min = g
            }
        }
        return min
    }
    func getLetterGrade(avg: Int64): String {
        return if (avg >= 90) {
            "A"
        } else if (avg >= 80) {
            "B"
        } else if (avg >= 70) {
            "C"
        } else if (avg >= 60) {
            "D"
        } else {
            "F"
        }
    }
    func printReport() {
        for (s in students) {
            let avg = getAverage(s.id)
            let hi = getHighest(s.id)
            let lo = getLowest(s.id)
            let letter = getLetterGrade(avg)
            println("${s.name} (ID=${s.id}): avg=${avg}, hi=${hi}, lo=${lo}, grade=${letter}")
        }
    }
}
