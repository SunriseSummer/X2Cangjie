fun main() {
    // mapIndexed
    val nums = listOf(10, 20, 30)
    val indexed = nums.mapIndexed { i, v -> i * 100 + v }
    println(indexed)  // [10, 120, 230]

    // filterNot
    val evens = listOf(1, 2, 3, 4, 5).filterNot { it % 2 != 0 }
    println(evens)  // [2, 4]

    // flatten
    val nested = listOf(listOf(1, 2), listOf(3, 4), listOf(5))
    val flat = nested.flatten()
    println(flat)  // [1, 2, 3, 4, 5]

    // forEach
    val items = listOf(1, 2, 3)
    var sum = 0
    items.forEach { sum += it }
    println(sum)  // 6

    // forEachIndexed
    val words = listOf("a", "b", "c")
    words.forEachIndexed { idx, w -> println("$idx:$w") }
    // 0:a
    // 1:b
    // 2:c

    // indexOfFirst / indexOfLast
    val data = listOf(1, 3, 5, 3, 1)
    val first3 = data.indexOfFirst { it == 3 }
    val last3 = data.indexOfLast { it == 3 }
    println("first3=$first3 last3=$last3")  // first3=1 last3=3

    // none
    val allPos = listOf(1, 2, 3).none { it < 0 }
    println("allPos=$allPos")  // allPos=true
}
