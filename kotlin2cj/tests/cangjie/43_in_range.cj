import std.collection.*

func classify(x: Int64): String {
    return if (x >= 0 && x <= 9) {
        "small"
    } else if (x >= 10 && x <= 99) {
        "medium"
    } else {
        "large"
    }
}

main() {
    for (v in ArrayList([3, 42, 500])) {
        println(classify(v))
    }
    let score = 75
    println(score >= 60 && score <= 100)
    println(!(score >= 0 && score <= 59))
    let xs = ArrayList([1, 2, 3])
    println(xs.contains(2))
    println(!(xs.contains(9)))
}
