func isEven(n: Int64): Bool {
    return n % 2 == 0
}

main() {
    for (i in 1..=6) {
        if (isEven(i)) {
            println("${i} even")
        } else {
            println("${i} odd")
        }
    }
    return 0
}
