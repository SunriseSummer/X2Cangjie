// Medium #1 (iter10): gradebook aggregation with optional lookups
class Student {
    let name: String
    var scores: [Int] = []
    init(_ name: String) { self.name = name }
    func add(_ score: Int) { scores.append(score) }
    func average() -> Int {
        if scores.count == 0 { return 0 }
        var total = 0
        for s in scores { total += s }
        return total / scores.count
    }
}

class Gradebook {
    var students: [String: Student] = [:]
    func addScore(_ name: String, _ score: Int) {
        let s = students[name]
        if let existing = s {
            existing.add(score)
        } else {
            let created = Student(name)
            created.add(score)
            students[name] = created
        }
    }
    func average(_ name: String) -> Int {
        let s = students[name]
        if let student = s { return student.average() }
        return 0
    }
    func report(_ names: [String]) {
        for n in names { print(n + "=" + "\(average(n))") }
    }
}

let g = Gradebook()
g.addScore("alice", 91)
g.addScore("bob", 75)
g.addScore("alice", 85)
g.addScore("carol", 99)
g.addScore("bob", 81)
g.report(["alice", "bob", "carol", "dave"])
