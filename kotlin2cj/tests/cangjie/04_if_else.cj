main() {
    let x = 7
    if (x > 10) {
        println("big")
    } else if (x > 5) {
        println("medium")
    } else {
        println("small")
    }
    let label = if ((x % 2) == 0) {
        "even"
    } else {
        "odd"
    }
    println(label)
}
