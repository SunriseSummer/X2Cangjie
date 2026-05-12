func grade(s: Int64): String {
    if (s>= 90) {
        return "A"
    } else if (s>= 80) {
        return "B"
    } else if (s>= 70) {
        return "C"
    } else {
        return "F"
    }
}

main() {
    println(grade(92))
    println(grade(81))
    println(grade(75))
    println(grade(40))
    return 0
}
