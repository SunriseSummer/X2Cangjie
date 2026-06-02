import std.collection.*

main() {
    let x = "hello"
    println(x.startsWith("he"))
    println(x.endsWith("lo"))
    println(x.contains("ell"))
    println(x.replace("l", "r"))
    let nums = ArrayList([1, 2, 3, 4, 5])
    let big = collectArrayList(nums.iterator().filter({ it => it > 3 }))
    println(String.join(collectArray<String>(big.iterator().map({e => e.toString()})), delimiter: ", "))
}
