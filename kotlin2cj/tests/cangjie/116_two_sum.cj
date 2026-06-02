import std.collection.*

func twoSum(nums: ArrayList<Int64>, target: Int64): String {
    let map = HashMap<Int64, Int64>()
    for (i in 0..nums.size) {
        let complement = target - nums[i]
        if (map.contains(complement)) {
            return "[${map[complement]}, ${i}]"
        }
        map[nums[i]] = i
    }
    return "[]"
}

main() {
    let a = ArrayList([2, 7, 11, 15])
    println("Two sum 9: ${twoSum(a, 9)}")
    let b = ArrayList([3, 2, 4])
    println("Two sum 6: ${twoSum(b, 6)}")
    let c = ArrayList([3, 3])
    println("Two sum 6: ${twoSum(c, 6)}")
}
