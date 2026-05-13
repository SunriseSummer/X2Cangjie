import std.collection.*

main() {
    var xs = ArrayList<Int64>([3, 1, 4, 1, 5, 9, 2, 6])
    var maxVal = xs[0]
    var minVal = xs[0]
    var sum = 0
    for (x in xs) {
        if (x > maxVal) {
            maxVal = x
        }
        if (x < minVal) {
            minVal = x
        }
        sum += x
    }
    println(maxVal)
    println(minVal)
    println(sum)
    return 0
}
