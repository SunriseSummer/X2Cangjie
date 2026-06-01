fun main() {
    var sum = 0
    for (i in 1..20) {
        if (i % 2 == 0) {
            continue
        }
        if (i > 10) {
            break
        }
        sum += i
    }
    println("sum=$sum")
}
