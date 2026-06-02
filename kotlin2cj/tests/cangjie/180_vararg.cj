func sum(nums: Array<Int64>): Int64 {
    var total = 0
    for (n in nums) {
        total += n
    }
    return total
}

func printAll(messages: Array<String>) {
    for (msg in messages) {
        println(msg)
    }
}

main() {
    println(sum(1, 2, 3, 4, 5))
    printAll("Hello", "World", "!")
}
