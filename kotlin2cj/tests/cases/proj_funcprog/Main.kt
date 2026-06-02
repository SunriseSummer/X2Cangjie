fun main() {
    val tools = FuncTools()
    val nums = arrayListOf(3, -1, 4, -1, 5, 9, -2, 6)

    val doubled = tools.doubleAll(nums)
    println("Doubled: ${doubled.joinToString(", ")}")

    val positive = tools.filterPositive(nums)
    println("Positive: ${positive.joinToString(", ")}")

    println("Sum: ${tools.sumAll(nums)}")

    val squared = tools.applyToEach(nums) { it * it }
    println("Squared: ${squared.joinToString(", ")}")

    val tripled = tools.applyToEach(nums) { it * 3 }
    println("Tripled: ${tripled.joinToString(", ")}")

    val firstNeg = tools.findFirst(nums) { it < 0 }
    println("First negative: $firstNeg")

    val firstBig = tools.findFirst(nums) { it > 7 }
    println("First > 7: $firstBig")

    val countPos = tools.countMatching(nums) { it > 0 }
    println("Count positive: $countPos")

    val countEven = tools.countMatching(nums) { it % 2 == 0 }
    println("Count even: $countEven")
}
