func classify(n: Int64): String {
    if (n < 0) {
        return "neg"
    } else if (n == 0) {
        return "zero"
    } else {
        return "pos"
    }
}

main() {
    println(classify( - 1))
    println(classify(0))
    println(classify(1))
    return 0
}
