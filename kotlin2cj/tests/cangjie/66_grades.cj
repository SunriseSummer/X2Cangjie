import std.collection.*

class Student <: ToString {
    let name: String
    let score: Int64
    init(name: String, score: Int64) {
        this.name = name
        this.score = score
    }
    public func toString(): String {
        return "Student(name=${this.name}, score=${this.score})"
    }
}

func grade(score: Int64): String {
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

main() {
    let students = ArrayList([Student("amy", 95), Student("ben", 82), Student("cara", 73), Student("dan", 60)])
    var total = 0
    for (s in students) {
        total = total + s.score
        println("${s.name}: ${grade(s.score)}")
    }
    let avg = total / students.size
    println("avg=${avg} grade=${grade(avg)}")
}
