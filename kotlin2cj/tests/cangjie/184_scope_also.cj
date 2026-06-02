import std.collection.*

main() {
    let nums = ArrayList([1, 2, 3])
    { =>
        let _also_list = nums
        let list = _also_list
        println("Size: ${list.size}")
        return _also_list
    }()
    println(String.join(collectArray<String>(nums.iterator().map({e => e.toString()})), delimiter: ", "))
}
