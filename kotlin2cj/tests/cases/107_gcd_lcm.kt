// GCD and LCM using Euclidean algorithm
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

fun lcm(a: Int, b: Int): Int {
    return a / gcd(a, b) * b
}

fun main() {
    println("gcd(12, 8) = ${gcd(12, 8)}")
    println("gcd(54, 24) = ${gcd(54, 24)}")
    println("gcd(7, 13) = ${gcd(7, 13)}")
    println("lcm(4, 6) = ${lcm(4, 6)}")
    println("lcm(12, 15) = ${lcm(12, 15)}")
    println("lcm(7, 5) = ${lcm(7, 5)}")
}
