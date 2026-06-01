// Two Sum using HashMap
fun twoSum(nums: ArrayList<Int>, target: Int): String {
    val map = HashMap<Int, Int>()
    for (i in 0 until nums.size) {
        val complement = target - nums[i]
        if (map.containsKey(complement)) {
            return "[${map[complement]}, $i]"
        }
        map[nums[i]] = i
    }
    return "[]"
}

fun main() {
    val a = arrayListOf(2, 7, 11, 15)
    println("Two sum 9: ${twoSum(a, 9)}")

    val b = arrayListOf(3, 2, 4)
    println("Two sum 6: ${twoSum(b, 6)}")

    val c = arrayListOf(3, 3)
    println("Two sum 6: ${twoSum(c, 6)}")
}
