// Strategy pattern with different sorting/comparison strategies
data class Student(val name: String, val grade: Int, val age: Int) {
    override fun toString(): String = "$name(g=$grade,a=$age)"
}

fun sortByGrade(students: ArrayList<Student>): ArrayList<Student> {
    val result = ArrayList<Student>()
    for (s in students) result.add(s)
    // Simple selection sort by grade descending
    for (i in 0 until result.size) {
        var maxIdx = i
        for (j in i + 1 until result.size) {
            if (result[j].grade > result[maxIdx].grade) {
                maxIdx = j
            }
        }
        if (maxIdx != i) {
            val tmp = result[i]
            result[i] = result[maxIdx]
            result[maxIdx] = tmp
        }
    }
    return result
}

fun sortByAge(students: ArrayList<Student>): ArrayList<Student> {
    val result = ArrayList<Student>()
    for (s in students) result.add(s)
    for (i in 0 until result.size) {
        var minIdx = i
        for (j in i + 1 until result.size) {
            if (result[j].age < result[minIdx].age) {
                minIdx = j
            }
        }
        if (minIdx != i) {
            val tmp = result[i]
            result[i] = result[minIdx]
            result[minIdx] = tmp
        }
    }
    return result
}

fun filterPassing(students: ArrayList<Student>, minGrade: Int): ArrayList<Student> {
    val result = ArrayList<Student>()
    for (s in students) {
        if (s.grade >= minGrade) result.add(s)
    }
    return result
}

fun main() {
    val students = arrayListOf(
        Student("Alice", 90, 20),
        Student("Bob", 75, 22),
        Student("Carol", 88, 19),
        Student("Dave", 92, 21),
        Student("Eve", 70, 23)
    )

    println("Original: ${students.joinToString(", ")}")
    println("By grade: ${sortByGrade(students).joinToString(", ")}")
    println("By age: ${sortByAge(students).joinToString(", ")}")

    val passing = filterPassing(students, 80)
    println("Passing (>=80): ${passing.joinToString(", ")}")
    println("Passing count: ${passing.size}")

    val avg = students.map { it.grade }.sum() / students.size
    println("Average grade: $avg")
}
