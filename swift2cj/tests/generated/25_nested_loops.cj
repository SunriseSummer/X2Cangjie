var s: Int64 = 0

main() {
    for (i in 1..=3) {
        for (j in 1..=3) {
            s = s + i * j
        }
    }
    println(s)
    return 0
}
