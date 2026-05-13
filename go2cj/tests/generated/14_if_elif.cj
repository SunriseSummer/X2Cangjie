func grade(s: Int64): String {
    if (s >= 90) {
        return "A"
    } else if (s >= 80) {
        return "B"
    } else if (s >= 70) {
        return "C"
    } else {
        return "F"
    }
}

main() {
    println(grade(95))
    println(grade(85))
    println(grade(75))
    println(grade(50))
    return 0
}
