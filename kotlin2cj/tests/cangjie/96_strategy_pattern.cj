import std.collection.*

class Student <: ToString {
    let name: String
    let grade: Int64
    let age: Int64
    init(name: String, grade: Int64, age: Int64) {
        this.name = name
        this.grade = grade
        this.age = age
    }
    public override func toString(): String {
        return "${name}(g=${grade},a=${age})"
    }
}

func sortByGrade(students: ArrayList<Student>): ArrayList<Student> {
    let result = ArrayList<Student>()
    for (s in students) {
        result.add(s)
    }
    for (i in 0..result.size) {
        var maxIdx = i
        for (j in (i + 1)..result.size) {
            if (result[j].grade > result[maxIdx].grade) {
                maxIdx = j
            }
        }
        if (maxIdx != i) {
            let tmp = result[i]
            result[i] = result[maxIdx]
            result[maxIdx] = tmp
        }
    }
    return result
}

func sortByAge(students: ArrayList<Student>): ArrayList<Student> {
    let result = ArrayList<Student>()
    for (s in students) {
        result.add(s)
    }
    for (i in 0..result.size) {
        var minIdx = i
        for (j in (i + 1)..result.size) {
            if (result[j].age < result[minIdx].age) {
                minIdx = j
            }
        }
        if (minIdx != i) {
            let tmp = result[i]
            result[i] = result[minIdx]
            result[minIdx] = tmp
        }
    }
    return result
}

func filterPassing(students: ArrayList<Student>, minGrade: Int64): ArrayList<Student> {
    let result = ArrayList<Student>()
    for (s in students) {
        if (s.grade >= minGrade) {
            result.add(s)
        }
    }
    return result
}

main() {
    let students = ArrayList([Student("Alice", 90, 20), Student("Bob", 75, 22), Student("Carol", 88, 19), Student("Dave", 92, 21), Student("Eve", 70, 23)])
    println("Original: ${String.join(collectArray<String>(students.iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("By grade: ${String.join(collectArray<String>(sortByGrade(students).iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("By age: ${String.join(collectArray<String>(sortByAge(students).iterator().map({e => e.toString()})), delimiter: ", ")}")
    let passing = filterPassing(students, 80)
    println("Passing (>=80): ${String.join(collectArray<String>(passing.iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("Passing count: ${passing.size}")
    let avg = collectArrayList(students.iterator().map({ it => it.grade })).iterator().fold<Int64>(0, {acc, x => acc + x}) / students.size
    println("Average grade: ${avg}")
}
