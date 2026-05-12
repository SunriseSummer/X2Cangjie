enum Shape {
    | circle
    | square
    | triangle
}

func name(s: Shape): String {
    match (s) {
        case circle =>
            return "C"
        case square =>
            return "S"
        case _ =>
            return "?"
    }
}

main() {
    println(name(circle))
    println(name(square))
    println(name(triangle))
    return 0
}
