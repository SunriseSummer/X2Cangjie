func sumOfDigits(n: Int64): Int64 {
    var x = n
    var sum = 0
    while (x > 0) {
        sum += x % 10
        x = x / 10
    }
    return sum
}

func power(base: Int64, exp: Int64): Int64 {
    var result = 1
    for (i in 0..exp) {
        result *= base
    }
    return result
}

main() {
    println("sumOfDigits(12345)=${sumOfDigits(12345)}")
    println("power(2,10)=${power(2, 10)}")
    println("power(3,4)=${power(3, 4)}")
}
