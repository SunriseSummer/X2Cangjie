class FuncTools {
    fun doubleAll(nums: ArrayList<Int>): ArrayList<Int> {
        val result = ArrayList<Int>()
        for (n in nums) {
            result.add(n * 2)
        }
        return result
    }

    fun filterPositive(nums: ArrayList<Int>): ArrayList<Int> {
        val result = ArrayList<Int>()
        for (n in nums) {
            if (n > 0) result.add(n)
        }
        return result
    }

    fun sumAll(nums: ArrayList<Int>): Int {
        var total = 0
        for (n in nums) {
            total += n
        }
        return total
    }

    fun applyToEach(nums: ArrayList<Int>, transform: (Int) -> Int): ArrayList<Int> {
        val result = ArrayList<Int>()
        for (n in nums) {
            result.add(transform(n))
        }
        return result
    }

    fun findFirst(nums: ArrayList<Int>, predicate: (Int) -> Boolean): Int {
        for (n in nums) {
            if (predicate(n)) return n
        }
        return -1
    }

    fun countMatching(nums: ArrayList<Int>, predicate: (Int) -> Boolean): Int {
        var count = 0
        for (n in nums) {
            if (predicate(n)) count++
        }
        return count
    }
}
