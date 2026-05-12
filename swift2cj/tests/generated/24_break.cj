var s: Int64 = 0

var t: Int64 = 0

main() {
    for (i in 0..20) {
        if (i == 5) {
            break
        }
        s = s + i
    }
    println(s)
    for (i in 0..10) {
        if (i % 2 == 0) {
            continue
        }
        t = t + i
    }
    println(t)
    return 0
}
