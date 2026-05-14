func swap(a: Int64, b: Int64): (Int64, Int64) {
    return (b, a)
}

main() {
    var x = 1
    var y = 2
    let r = swap(x, y)
    x = r[0]
    y = r[1]
    println(x)
    println(y)
    return 0
}
