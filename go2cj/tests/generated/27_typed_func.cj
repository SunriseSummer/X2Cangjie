func max(a: Int64, b: Int64): Int64 {
    if (a > b) {
        return a
    }
    return b
}

main() {
    println(max(3, 7))
    println(max(10, 2))
    return 0
}
