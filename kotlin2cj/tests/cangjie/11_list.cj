import std.collection.*

main() {
    let nums = ArrayList([1, 2, 3])
    nums.add(4)
    nums.add(5)
    var total = 0
    for (x in nums) {
        total += x
    }
    println("size=${nums.size} total=${total} first=${nums[0]}")
}
