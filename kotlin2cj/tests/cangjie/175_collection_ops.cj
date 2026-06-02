import std.collection.*
import std.sort.*

main() {
    let numbers = ArrayList([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    let evenDoubled = collectArrayList(collectArrayList(numbers.iterator().filter({ it => (it % 2) == 0 })).iterator().map({ it => it * 2 }))
    println("evenDoubled: ${String.join(collectArray<String>(evenDoubled.iterator().map({e => e.toString()})), delimiter: ", ")}")
    let first3 = collectArrayList(numbers.iterator().take(3))
    let rest = collectArrayList(numbers.iterator().skip(3))
    println("first3: ${String.join(collectArray<String>(first3.iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("rest: ${String.join(collectArray<String>(rest.iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("any > 5: ${numbers.iterator().any({ it => it > 5 })}")
    println("all > 0: ${numbers.iterator().all({ it => it > 0 })}")
    let sum = numbers.iterator().fold<Int64>(0, { acc, x => acc + x })
    println("fold sum: ${sum}")
    let product = collectArrayList(numbers.iterator().take(5)).iterator().reduce({ acc, x => acc * x }).getOrThrow()
    println("reduce product(1..5): ${product}")
    let unsorted = ArrayList([5, 3, 1, 4, 2])
    println("sorted: ${String.join(collectArray<String>(({ => let _s = collectArrayList(unsorted.iterator()); sort(_s, stable: true); _s })().iterator().map({e => e.toString()})), delimiter: ", ")}")
    println("sortedDescending: ${String.join(collectArray<String>(({ => let _s = collectArrayList(unsorted.iterator()); sort(_s, stable: true, descending: true); _s })().iterator().map({e => e.toString()})), delimiter: ", ")}")
}
