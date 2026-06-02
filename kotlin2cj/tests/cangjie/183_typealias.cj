import std.collection.*

main() {
    let nums: ArrayList<Int64> = ArrayList([1, 2, 3])
    println(nums.size)
    for (n in nums) {
        print("${n} ")
    }
    println()
}

// typealias IntList = ArrayList<Int64>
