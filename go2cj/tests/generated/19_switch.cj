func dayName(d: Int64): String {
    match (d) {
        case 1 =>
            return "Mon"
        case 2 =>
            return "Tue"
        case 3 =>
            return "Wed"
        case _ =>
            return "?"
    }
}

main() {
    println(dayName(1))
    println(dayName(2))
    println(dayName(3))
    println(dayName(7))
    return 0
}
