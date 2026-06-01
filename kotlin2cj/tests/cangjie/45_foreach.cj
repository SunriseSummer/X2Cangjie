import std.collection.*

main() {
    let nums = ArrayList([1, 2, 3, 4, 5])
    var sum = 0
    for (n in nums) {
        sum += n
    }
    println("sum=${sum}")
    var product = 1
    for (it in nums) {
        product *= it
    }
    println("product=${product}")
}
