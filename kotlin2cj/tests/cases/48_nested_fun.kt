fun outer(n: Int): Int {
    fun square(x: Int): Int {
        return x * x
    }
    var total = 0
    for (i in 1..n) {
        total += square(i)
    }
    return total
}
fun main() {
    println(outer(3))
    println(outer(5))
}
