func outer(n: Int64): Int64 {
    func square(x: Int64): Int64 {
        return x * x
    }
    var total = 0
    for (i in 1..=n) {
        total += square(i)
    }
    return total
}

main() {
    println(outer(3))
    println(outer(5))
}
