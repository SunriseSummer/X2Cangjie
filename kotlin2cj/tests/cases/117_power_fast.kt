// Fast Exponentiation (Binary method)
fun power(base: Long, exp: Int, mod: Long): Long {
    var result = 1L
    var b = base % mod
    var e = exp
    while (e > 0) {
        if (e % 2 == 1) {
            result = result * b % mod
        }
        e = e / 2
        b = b * b % mod
    }
    return result
}

fun main() {
    println("2^10 mod 1000 = ${power(2, 10, 1000)}")
    println("3^13 mod 100 = ${power(3, 13, 100)}")
    println("5^0 mod 7 = ${power(5, 0, 7)}")
    println("7^3 mod 1000 = ${power(7, 3, 1000)}")
}
