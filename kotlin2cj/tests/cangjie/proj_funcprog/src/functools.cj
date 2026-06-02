package proj_funcprog

import std.collection.*

class FuncTools {
    func doubleAll(nums: ArrayList<Int64>): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        for (n in nums) {
            result.add(n * 2)
        }
        return result
    }
    func filterPositive(nums: ArrayList<Int64>): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        for (n in nums) {
            if (n > 0) {
                result.add(n)
            }
        }
        return result
    }
    func sumAll(nums: ArrayList<Int64>): Int64 {
        var total = 0
        for (n in nums) {
            total += n
        }
        return total
    }
    func applyToEach(nums: ArrayList<Int64>, transform: (Int64) -> Int64): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        for (n in nums) {
            result.add(transform(n))
        }
        return result
    }
    func findFirst(nums: ArrayList<Int64>, predicate: (Int64) -> Bool): Int64 {
        for (n in nums) {
            if (predicate(n)) {
                return n
            }
        }
        return -1
    }
    func countMatching(nums: ArrayList<Int64>, predicate: (Int64) -> Bool): Int64 {
        var count = 0
        for (n in nums) {
            if (predicate(n)) {
                count += 1
            }
        }
        return count
    }
}
