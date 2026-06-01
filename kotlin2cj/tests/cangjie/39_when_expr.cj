func sign(x: Int64): String {
    let s = if (x > 0) {
        "positive"
    } else if (x < 0) {
        "negative"
    } else {
        "zero"
    }
    return s
}

main() {
    println(sign(7))
    println(sign(-3))
    println(sign(0))
}
