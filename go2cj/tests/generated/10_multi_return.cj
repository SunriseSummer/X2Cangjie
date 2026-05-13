func swap(a: Int64, b: Int64): (Int64, Int64) {
    return (b, a)
}

main() {
    let (x, y) = (swap(1, 2))
    println(x)
    println(y)
    return 0
}
