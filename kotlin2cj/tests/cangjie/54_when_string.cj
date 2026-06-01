import std.collection.*

func gradePoint(letter: String): Int64 {
    return match (letter) {
        case "A" => 4
        case "B" => 3
        case "C" | "D" => 2
        case _ => 0}
}

main() {
    let grades = ArrayList(["A", "B", "C", "D", "F"])
    var sum = 0
    for (g in grades) {
        sum += gradePoint(g)
    }
    println("sum=${sum}")
    for (g in grades) {
        println("${g} -> ${gradePoint(g)}")
    }
}
