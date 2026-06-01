import std.collection.*

main() {
    let a = 3
    let b = 7
    println((if (a > b) { a } else { b }))
    println((if (a < b) { a } else { b }))
    println((if (10 > (if (4 < 9) { 4 } else { 9 })) { 10 } else { (if (4 < 9) { 4 } else { 9 }) }))
    var best = 0
    for (x in ArrayList([5, 2, 8, 1])) {
        best = (if (best > x) { best } else { x })
    }
    println(best)
}
