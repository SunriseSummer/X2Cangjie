fun main() {
    val nums = mutableListOf(1, 2, 3)
    nums.also { list ->
        println("Size: ${list.size}")
    }
    println(nums.joinToString(", "))
}
