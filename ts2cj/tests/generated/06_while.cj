var n: Int64 = 5

var acc: Int64 = 0

main() {
    while (n > 0) {
        acc = acc + n
        n = n - 1
    }
    println("acc=${acc}")
    return 0
}
