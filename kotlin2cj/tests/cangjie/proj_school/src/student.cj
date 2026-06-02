package proj_school

import std.collection.*

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
