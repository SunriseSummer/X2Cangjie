// ~450 line mixed program: a small "school" domain exercising many idioms.

enum class Subject { MATH, SCIENCE, HISTORY, ART, MUSIC }

data class Student(val id: Int, val name: String, val grade: Int)

data class Score(val student: Student, val subject: Subject, val points: Int)

fun letterGrade(score: Int): String = when (score) {
    in 90..100 -> "A"
    in 80..89 -> "B"
    in 70..79 -> "C"
    in 60..69 -> "D"
    !in 0..100 -> "?"
    else -> "F"
}

class Gradebook {
    val scores = ArrayList<Score>()

    fun record(student: Student, subject: Subject, points: Int) {
        scores.add(Score(student, subject, points))
    }

    fun recordAll(more: List<Score>) {
        scores.addAll(more)
    }

    fun forStudent(s: Student): List<Score> {
        val out = ArrayList<Score>()
        for (sc in scores) {
            if (sc.student.id == s.id) {
                out.add(sc)
            }
        }
        return out
    }

    fun forSubject(sub: Subject): List<Score> {
        val out = ArrayList<Score>()
        for (sc in scores) {
            if (sc.subject == sub) {
                out.add(sc)
            }
        }
        return out
    }

    fun average(student: Student): Int {
        val mine = forStudent(student)
        if (mine.isEmpty()) {
            return 0
        }
        var total = 0
        for (sc in mine) {
            total = total + sc.points
        }
        return total / mine.size
    }

    fun topPoints(): Int {
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

    fun topName(): String {
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

    fun count(): Int {
        return scores.size
    }
}

fun describe(s: Student): String {
    return "Student #" + s.id + " " + s.name + " (grade " + s.grade + ")"
}

fun applyBonus(points: Int, bonus: Int): Int {
    return points + bonus
}

fun transform(values: List<Int>, f: (Int) -> Int): List<Int> {
    val out = ArrayList<Int>()
    for (v in values) {
        out.add(f(v))
    }
    return out
}

fun sumOfList(values: List<Int>): Int {
    var total = 0
    for (v in values) {
        total = total + v
    }
    return total
}

fun maxOfList(values: List<Int>): Int {
    var m = values[0]
    for (v in values) {
        if (v > m) {
            m = v
        }
    }
    return m
}

fun subjectName(sub: Subject): String = when (sub) {
    Subject.MATH -> "Mathematics"
    Subject.SCIENCE -> "Science"
    Subject.HISTORY -> "History"
    Subject.ART -> "Art"
    Subject.MUSIC -> "Music"
}

fun main() {
    val alice = Student(1, "Alice", 10)
    val bob = Student(2, "Bob", 11)
    val carol = Student(3, "Carol", 10)

    println(describe(alice))
    println(describe(bob))
    println(describe(carol))
    println(alice)

    val book = Gradebook()
    book.record(alice, Subject.MATH, 95)
    book.record(alice, Subject.SCIENCE, 88)
    book.record(alice, Subject.HISTORY, 73)
    book.record(bob, Subject.MATH, 64)
    book.record(bob, Subject.ART, 91)
    book.record(carol, Subject.MUSIC, 55)

    val extra = ArrayList<Score>()
    extra.add(Score(carol, Subject.MATH, 82))
    extra.add(Score(carol, Subject.SCIENCE, 77))
    book.recordAll(extra)

    println("Total scores recorded: " + book.count())

    val students = listOf(alice, bob, carol)
    for (s in students) {
        val avg = book.average(s)
        println(s.name + " avg=" + avg + " -> " + letterGrade(avg))
    }

    for (s in students) {
        val mine = book.forStudent(s)
        val parts = ArrayList<String>()
        for (sc in mine) {
            parts.add(subjectName(sc.subject) + ":" + sc.points)
        }
        println(s.name + " => " + parts.joinToString(", "))
    }

    println("Top: " + book.topName() + " " + book.topPoints())

    val raw = listOf(5, 3, 9, 1, 7, 2, 8)
    val doubled = transform(raw) { it * 2 }
    println("doubled=" + doubled.joinToString(" "))
    println("sum=" + sumOfList(raw))
    println("max=" + maxOfList(raw))

    val sortable = ArrayList<Int>()
    for (v in raw) {
        sortable.add(v)
    }
    sortable.sort()
    println("sorted=" + sortable.joinToString(" "))
    sortable.sortDescending()
    println("desc=" + sortable.joinToString(" "))

    val mathScores = book.forSubject(Subject.MATH)
    var mathTotal = 0
    for (sc in mathScores) {
        mathTotal = mathTotal + sc.points
    }
    println("math entries=" + mathScores.size + " total=" + mathTotal)

    val grades = listOf(45, 65, 72, 88, 91, 100, 130)
    for (g in grades) {
        println(g.toString() + " -> " + letterGrade(g))
    }

    val counts = HashMap<String, Int>()
    for (s in scores(book)) {
        val k = subjectName(s.subject)
        counts[k] = (counts[k] ?: 0) + 1
    }
    val keys = ArrayList<String>()
    for (k in counts.keys) {
        keys.add(k)
    }
    keys.sort()
    for (k in keys) {
        println(k + " has " + counts[k] + " score(s)")
    }
}

fun scores(book: Gradebook): List<Score> {
    return book.scores
}
