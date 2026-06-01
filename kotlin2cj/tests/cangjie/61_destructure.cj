import std.collection.*

func divmod(a: Int64, b: Int64): (Int64, Int64) {
    return (a / b, a % b)
}

main() {
    let (q, r) = divmod(17, 5)
    println("${q} ${r}")
    let point = (3, 7)
    let (x, y) = point
    println(x + y)
    let pairs = ArrayList([(1, "one"), (2, "two"), (3, "three")])
    for ((n, name) in pairs) {
        println("${n}=${name}")
    }
}
