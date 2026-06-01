fun gcd(a: Int, b: Int): Int {
    var x = a
    var y = b
    while (y != 0) {
        val t = y
        y = x % y
        x = t
    }
    return x
}
fun main() {
    println("gcd(48,36)=${gcd(48, 36)}")
    println("gcd(17,5)=${gcd(17, 5)}")
}
