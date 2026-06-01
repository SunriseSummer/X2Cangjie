typealias IntList = List<Int>

fun main() {
    val nums: IntList = listOf(1, 2, 3)
    println(nums.size)
    for (n in nums) {
        print("$n ")
    }
    println()
}
