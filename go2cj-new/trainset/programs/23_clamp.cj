func clamp(x: Int64, lo: Int64, hi: Int64): Int64 {
    if (x < lo) {
        return lo
    }
    if (x > hi) {
        return hi
    }
    return x
}

main() {
    println(clamp(5, 0, 10))
    println(clamp(-3, 0, 10))
    println(clamp(15, 0, 10))
    return 0
}
