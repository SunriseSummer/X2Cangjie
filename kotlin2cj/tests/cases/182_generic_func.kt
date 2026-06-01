fun <T> first(list: List<T>): T {
    return list[0]
}

fun <T> lastIndex(list: List<T>): Int {
    return list.size - 1
}

fun main() {
    val nums = listOf(10, 20, 30)
    println(first(nums))
    println(lastIndex(nums))

    val strs = listOf("a", "b", "c")
    println(first(strs))
}
