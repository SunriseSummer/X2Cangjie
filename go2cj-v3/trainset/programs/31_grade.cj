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
    println(grade(91))
    println(grade(82))
    println(grade(73))
    println(grade(60))
    return 0
}
