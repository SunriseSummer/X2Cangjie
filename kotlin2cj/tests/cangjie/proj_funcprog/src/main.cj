package proj_funcprog

import std.collection.*

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
