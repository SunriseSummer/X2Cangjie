import std.collection.*

main() {
    let m = ArrayList([ArrayList([1, 2, 3]), ArrayList([4, 5, 6])])
    var sum = 0
    for (row in m) {
        for (v in row) {
            sum += v
        }
    }
    println("sum=${sum}")
    println("m[1][2]=${m[1][2]}")
}
