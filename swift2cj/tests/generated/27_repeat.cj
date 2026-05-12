var n: Int64 = 1

var p: Int64 = 1

main() {
    do {
        p = p * n
        n = n + 1
    } while (n <= 5)
    println(p)
    return 0
}
