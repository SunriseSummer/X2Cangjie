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

main() {
    let tools = FuncTools()
    let nums = ArrayList([3, -1, 4, -1, 5, 9, -2, 6])
    let doubled = tools.doubleAll(nums)
    println("Doubled: ${String.join(collectArray<String>(doubled.iterator().map({e => e.toString()})), delimiter: ", ")}")
    let positive = tools.filterPositive(nums)
    println("Positive: ${String.join(collectArray<String>(positive.iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("Sum: ${tools.sumAll(nums)}")
    let squared = tools.applyToEach(nums, { it => it * it })
    println("Squared: ${String.join(collectArray<String>(squared.iterator().map({e => e.toString()})), delimiter: ", ")}")
    let tripled = tools.applyToEach(nums, { it => it * 3 })
    println("Tripled: ${String.join(collectArray<String>(tripled.iterator().map({e => e.toString()})), delimiter: ", ")}")
    let firstNeg = tools.findFirst(nums, { it => it < 0 })
    println("First negative: ${firstNeg}")
    let firstBig = tools.findFirst(nums, { it => it > 7 })
    println("First > 7: ${firstBig}")
    let countPos = tools.countMatching(nums, { it => it > 0 })
    println("Count positive: ${countPos}")
    let countEven = tools.countMatching(nums, { it => (it % 2) == 0 })
    println("Count even: ${countEven}")
}