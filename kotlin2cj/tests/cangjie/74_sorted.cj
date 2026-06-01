import std.collection.*
import std.sort.*

main() {
    let grades = ArrayList([85, 92, 78, 64, 99, 73, 88])
    let sorted = ({ => let _s = collectArrayList(grades.iterator()); sort(_s, stable: true, descending: true); _s })()
    print("ranked: ")
    for (g in sorted) {
        print("${g} ")
    }
    println()
    println("avg=${grades.iterator().fold<Int64>(0, {acc, x => acc + x}) / grades.size}")
}
