import std.collection.*
import std.deriving.*
import std.sort.*

@Derive[Equatable]
enum Subject <: ToString {
    | MATH | SCIENCE | HISTORY | ART | MUSIC
    public func toString(): String {
    return match (this) {
                case MATH => "MATH"
            case SCIENCE => "SCIENCE"
            case HISTORY => "HISTORY"
            case ART => "ART"
            case MUSIC => "MUSIC"
}
    }
}

class Student <: ToString {
    let id: Int64
    let name: String
    let grade: Int64
    init(id: Int64, name: String, grade: Int64) {
        this.id = id
        this.name = name
        this.grade = grade
    }
    public func toString(): String {
        return "Student(id=${this.id}, name=${this.name}, grade=${this.grade})"
    }
}

class Score <: ToString {
    let student: Student
    let subject: Subject
    let points: Int64
    init(student: Student, subject: Subject, points: Int64) {
        this.student = student
        this.subject = subject
        this.points = points
    }
    public func toString(): String {
        return "Score(student=${this.student}, subject=${this.subject}, points=${this.points})"
    }
}

func letterGrade(score: Int64): String {
    return if (score >= 90 && score <= 100) {
        "A"
    } else if (score >= 80 && score <= 89) {
        "B"
    } else if (score >= 70 && score <= 79) {
        "C"
    } else if (score >= 60 && score <= 69) {
        "D"
    } else if (!(score >= 0 && score <= 100)) {
        "?"
    } else {
        "F"
    }
}

class Gradebook {
    let scores = ArrayList<Score>()
    func record(student: Student, subject: Subject, points: Int64) {
        scores.add(Score(student, subject, points))
    }
    func recordAll(more: ArrayList<Score>) {
        scores.add(all: more)
    }
    func forStudent(s: Student): ArrayList<Score> {
        let out = ArrayList<Score>()
        for (sc in scores) {
            if (sc.student.id == s.id) {
                out.add(sc)
            }
        }
        return out
    }
    func forSubject(sub: Subject): ArrayList<Score> {
        let out = ArrayList<Score>()
        for (sc in scores) {
            if (sc.subject == sub) {
                out.add(sc)
            }
        }
        return out
    }
    func average(student: Student): Int64 {
        let mine = forStudent(student)
        if (mine.isEmpty()) {
            return 0
        }
        var total = 0
        for (sc in mine) {
            total = total + sc.points
        }
        return total / mine.size
    }
    func topPoints(): Int64 {
        if (scores.isEmpty()) {
            return 0
        }
        var best = scores[0].points
        for (sc in scores) {
            if (sc.points > best) {
                best = sc.points
            }
        }
        return best
    }
    func topName(): String {
        if (scores.isEmpty()) {
            return "-"
        }
        var bestIdx = 0
        var i = 0
        for (sc in scores) {
            if (sc.points > scores[bestIdx].points) {
                bestIdx = i
            }
            i = i + 1
        }
        return scores[bestIdx].student.name
    }
    func count(): Int64 {
        return scores.size
    }
}

func describe(s: Student): String {
    return ((((("Student #" + s.id.toString()) + " ") + s.name.toString()) + " (grade ") + s.grade.toString()) + ")"
}

func applyBonus(points: Int64, bonus: Int64): Int64 {
    return points + bonus
}

func transform(values: ArrayList<Int64>, f: (Int64) -> Int64): ArrayList<Int64> {
    let out = ArrayList<Int64>()
    for (v in values) {
        out.add(f(v))
    }
    return out
}

func sumOfList(values: ArrayList<Int64>): Int64 {
    var total = 0
    for (v in values) {
        total = total + v
    }
    return total
}

func maxOfList(values: ArrayList<Int64>): Int64 {
    var m = values[0]
    for (v in values) {
        if (v > m) {
            m = v
        }
    }
    return m
}

func subjectName(sub: Subject): String {
    return match (sub) {
        case Subject.MATH => "Mathematics"
        case Subject.SCIENCE => "Science"
        case Subject.HISTORY => "History"
        case Subject.ART => "Art"
        case Subject.MUSIC => "Music"}
}

main() {
    let alice = Student(1, "Alice", 10)
    let bob = Student(2, "Bob", 11)
    let carol = Student(3, "Carol", 10)
    println(describe(alice))
    println(describe(bob))
    println(describe(carol))
    println(alice)
    let book = Gradebook()
    book.record(alice, Subject.MATH, 95)
    book.record(alice, Subject.SCIENCE, 88)
    book.record(alice, Subject.HISTORY, 73)
    book.record(bob, Subject.MATH, 64)
    book.record(bob, Subject.ART, 91)
    book.record(carol, Subject.MUSIC, 55)
    let extra = ArrayList<Score>()
    extra.add(Score(carol, Subject.MATH, 82))
    extra.add(Score(carol, Subject.SCIENCE, 77))
    book.recordAll(extra)
    println("Total scores recorded: " + book.count().toString())
    let students = ArrayList([alice, bob, carol])
    for (s in students) {
        let avg = book.average(s)
        println((((s.name.toString() + " avg=") + avg.toString()) + " -> ") + letterGrade(avg).toString())
    }
    for (s in students) {
        let mine = book.forStudent(s)
        let parts = ArrayList<String>()
        for (sc in mine) {
            parts.add((subjectName(sc.subject).toString() + ":") + sc.points.toString())
        }
        println((s.name.toString() + " => ") + String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: ", "))
    }
    println((("Top: " + book.topName().toString()) + " ") + book.topPoints().toString())
    let raw = ArrayList([5, 3, 9, 1, 7, 2, 8])
    let doubled = transform(raw, { it => it * 2 })
    println("doubled=" + String.join(collectArray<String>(doubled.iterator().map({e => e.toString()})), delimiter: " "))
    println("sum=" + sumOfList(raw).toString())
    println("max=" + maxOfList(raw).toString())
    let sortable = ArrayList<Int64>()
    for (v in raw) {
        sortable.add(v)
    }
    sort(sortable, stable: true)
    println("sorted=" + String.join(collectArray<String>(sortable.iterator().map({e => e.toString()})), delimiter: " "))
    sort(sortable, stable: true, descending: true)
    println("desc=" + String.join(collectArray<String>(sortable.iterator().map({e => e.toString()})), delimiter: " "))
    let mathScores = book.forSubject(Subject.MATH)
    var mathTotal = 0
    for (sc in mathScores) {
        mathTotal = mathTotal + sc.points
    }
    println((("math entries=" + mathScores.size.toString()) + " total=") + mathTotal.toString())
    let grades = ArrayList([45, 65, 72, 88, 91, 100, 130])
    for (g in grades) {
        println((g.toString() + " -> ") + letterGrade(g).toString())
    }
    let counts = HashMap<String, Int64>()
    for (s in scores(book)) {
        let k = subjectName(s.subject)
        counts[k] = (counts.get(k) ?? 0) + 1
    }
    let keys = ArrayList<String>()
    for (k in counts.keys()) {
        keys.add(k)
    }
    sort(keys, stable: true)
    for (k in keys) {
        println(((k + " has ") + counts[k].toString()) + " score(s)")
    }
}

func scores(book: Gradebook): ArrayList<Score> {
    return book.scores
}
