fun main() {
    val fibs = mutableListOf(0, 1)
    for (i in 2 until 12) {
        val next = fibs[i - 1] + fibs[i - 2]
        fibs.add(next)
    }
    for (x in fibs) {
        print("$x ")
    }
    println("")
    println("last=${fibs[fibs.size - 1]}")
}
