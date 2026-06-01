fun sumOfDigits(n: Int): Int {
    var x = n
    var sum = 0
    while (x > 0) {
        sum += x % 10
        x = x / 10
    }
    return sum
}
fun power(base: Int, exp: Int): Int {
    var result = 1
    for (i in 0 until exp) {
        result *= base
    }
    return result
}
fun main() {
    println("sumOfDigits(12345)=${sumOfDigits(12345)}")
    println("power(2,10)=${power(2, 10)}")
    println("power(3,4)=${power(3, 4)}")
}
