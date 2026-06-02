import std.collection.*

func first<T>(list: ArrayList<T>): T {
    return list[0]
}

func lastIndex<T>(list: ArrayList<T>): Int64 {
    return list.size - 1
}

main() {
    let nums = ArrayList([10, 20, 30])
    println(first(nums))
    println(lastIndex(nums))
    let strs = ArrayList(["a", "b", "c"])
    println(first(strs))
}
