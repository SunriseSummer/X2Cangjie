import std.collection.*

func classify(t: Int64): String {
    return if (t < 0) {
        "freezing"
    } else if (t < 15) {
        "cold"
    } else if (t < 25) {
        "mild"
    } else {
        "hot"
    }
}

main() {
    let temps = ArrayList([-5, 10, 20, 30])
    for (t in temps) {
        println("${t}: ${classify(t)}")
    }
}
