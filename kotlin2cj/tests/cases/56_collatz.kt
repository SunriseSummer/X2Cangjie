fun collatzLength(start: Int): Int {
    var n = start
    var steps = 0
    while (n != 1) {
        if (n % 2 == 0) {
            n = n / 2
        } else {
            n = 3 * n + 1
        }
        steps += 1
    }
    return steps
}
fun main() {
    var best = 0
    var bestLen = 0
    for (i in 1..30) {
        val len = collatzLength(i)
        if (len > bestLen) {
            bestLen = len
            best = i
        }
    }
    println("best=$best len=$bestLen")
    println(collatzLength(27))
}
