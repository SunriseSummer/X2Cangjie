// Test: Complex multi-return logic with nested conditions
fun classify(score: Int): String {
    if (score < 0 || score > 100) return "Invalid"
    if (score >= 90) return "A"
    if (score >= 80) return "B"
    if (score >= 70) return "C"
    if (score >= 60) return "D"
    return "F"
}

fun findFirst(arr: ArrayList<Int>, predicate: (Int) -> Boolean): Int {
    for (i in 0..arr.size - 1) {
        if (predicate(arr[i])) return i
    }
    return -1
}

fun sumUntil(limit: Int): Int {
    var sum = 0
    var i = 1
    while (sum < limit) {
        sum += i
        i++
    }
    return sum
}

fun main() {
    println(classify(95))
    println(classify(82))
    println(classify(71))
    println(classify(55))
    println(classify(-5))

    val nums = arrayListOf(3, 7, 2, 9, 4, 6)
    println(findFirst(nums) { it > 5 })
    println(findFirst(nums) { it > 10 })

    println(sumUntil(10))
    println(sumUntil(50))
}
