fun main() {
    val nums = listOf(1, 2, 3, 4, 5)
    var sum = 0
    nums.forEach { n ->
        sum += n
    }
    println("sum=$sum")
    var product = 1
    nums.forEach {
        product *= it
    }
    println("product=$product")
}
