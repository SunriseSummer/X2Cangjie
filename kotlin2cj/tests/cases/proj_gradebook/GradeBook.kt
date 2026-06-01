data class Student(val name: String, val id: Int)

class GradeBook {
    val students = mutableListOf<Student>()
    val grades = HashMap<Int, ArrayList<Int>>()

    fun addStudent(name: String, id: Int) {
        students.add(Student(name, id))
        grades[id] = ArrayList<Int>()
    }

    fun addGrade(studentId: Int, grade: Int) {
        grades[studentId]!!.add(grade)
    }

    fun getAverage(studentId: Int): Int {
        val list = grades[studentId]!!
        if (list.isEmpty()) return 0
        var sum = 0
        for (g in list) {
            sum += g
        }
        return sum / list.size
    }

    fun getHighest(studentId: Int): Int {
        val list = grades[studentId]!!
        if (list.isEmpty()) return 0
        var max = list[0]
        for (g in list) {
            if (g > max) max = g
        }
        return max
    }

    fun getLowest(studentId: Int): Int {
        val list = grades[studentId]!!
        if (list.isEmpty()) return 0
        var min = list[0]
        for (g in list) {
            if (g < min) min = g
        }
        return min
    }

    fun getLetterGrade(avg: Int): String = when {
        avg >= 90 -> "A"
        avg >= 80 -> "B"
        avg >= 70 -> "C"
        avg >= 60 -> "D"
        else -> "F"
    }

    fun printReport() {
        for (s in students) {
            val avg = getAverage(s.id)
            val hi = getHighest(s.id)
            val lo = getLowest(s.id)
            val letter = getLetterGrade(avg)
            println("${s.name} (ID=${s.id}): avg=$avg, hi=$hi, lo=$lo, grade=$letter")
        }
    }
}
