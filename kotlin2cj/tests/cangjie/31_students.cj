import std.collection.*

class Student {
    let name: String
    let score: Int64
    init(name: String, score: Int64) {
        this.name = name
        this.score = score
    }
    func grade(): String {
        return if (score >= 90) {
            "A"
        } else if (score >= 80) {
            "B"
        } else if (score >= 70) {
            "C"
        } else {
            "F"
        }
    }
}

func average(students: ArrayList<Student>): Int64 {
    var sum = 0
    for (s in students) {
        sum += s.score
    }
    return sum / students.size
}

main() {
    let students = ArrayList([Student("alice", 92), Student("bob", 78), Student("carol", 85), Student("dave", 60)])
    for (s in students) {
        println("${s.name}: ${s.score} (${s.grade()})")
    }
    println("average=${average(students)}")
}
