func divmod(a: Int64, b: Int64): (Int64, Int64) {
    return (a / b, a % b)
}

main() {
    var (q, r) = divmod(17, 5)
    println(q)
    println(r)
    return 0
}
