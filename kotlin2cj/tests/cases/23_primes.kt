fun isPrime(n: Int): Boolean {
    if (n < 2) {
        return false
    }
    var i = 2
    while (i * i <= n) {
        if (n % i == 0) {
            return false
        }
        i += 1
    }
    return true
}
fun main() {
    var count = 0
    for (n in 2..30) {
        if (isPrime(n)) {
            count += 1
            print("$n ")
        }
    }
    println("")
    println("count=$count")
}
