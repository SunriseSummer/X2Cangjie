import std.collection.*

main() {
    let nums = ArrayList([3, 1, 4, 1, 5, 9, 2, 6])
    for (x in collectArrayList(collectArrayList(nums.iterator().filter({ it => (it % 2) == 0 })).iterator().map({ it => it * it }))) {
        print("${x} ")
    }
    println()
    let s = collectArrayList(nums.iterator().filter({ it => it > 2 })).iterator().fold<Int64>(0, {acc, x => acc + x})
    println("sum=${s}")
    println("any=${nums.iterator().any({ it => it > 8 })} all=${nums.iterator().all({ it => it > 0 })} none=${!nums.iterator().any({ it => it > 100 })}")
    println("evens=${nums.iterator().filter({ it => (it % 2) == 0 }).count()}")
    let words = ArrayList(["apple", "fig", "cherry"])
    println("totlen=${words.iterator().map({ it => it.size }).fold<Int64>(0, {acc, x => acc + x})}")
    let folded = nums.iterator().fold<Int64>(100, { acc, n => acc + n })
    println("folded=${folded}")
    println("reduced=${nums.iterator().reduce({ a, b => a + b }).getOrThrow()}")
    println("max=${nums.iterator().reduce({a, b => if (a > b) { a } else { b }}) ?? 0} min=${nums.iterator().reduce({a, b => if (a < b) { a } else { b }}) ?? 0}")
    println(String.join(collectArray<String>(words.iterator().map({ it => it.toAsciiUpper() })), delimiter: ", "))
}
