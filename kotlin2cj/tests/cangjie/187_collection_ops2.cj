import std.collection.*

main() {
    let nums = ArrayList([10, 20, 30])
    let indexed = collectArrayList(nums.iterator().enumerate().map({ _p => ({ i, v => (i * 100) + v })(_p[0], _p[1]) }))
    println(indexed)
    let evens = collectArrayList(ArrayList([1, 2, 3, 4, 5]).iterator().filter({ _e => !({ it => (it % 2) != 0 })(_e) }))
    println(evens)
    let nested = ArrayList([ArrayList([1, 2]), ArrayList([3, 4]), ArrayList([5])])
    let flat = collectArrayList(nested.iterator().flatMap({ _e => _e.iterator() }))
    println(flat)
    let items = ArrayList([1, 2, 3])
    var sum = 0
    for (it in items) {
        sum += it
    }
    println(sum)
    let words = ArrayList(["a", "b", "c"])
    for ((idx, w) in words.iterator().enumerate()) {
        println("${idx}:${w}")
    }
    let data = ArrayList([1, 3, 5, 3, 1])
    let first3 = ({ => var _i = 0; for (_e in data) { if (({ it => it == 3 })(_e)) { return _i }; _i++ }; return -1 })()
    let last3 = ({ => var _r = -1; var _i = 0; for (_e in data) { if (({ it => it == 3 })(_e)) { _r = _i }; _i++ }; return _r })()
    println("first3=${first3} last3=${last3}")
    let allPos = !ArrayList([1, 2, 3]).iterator().any({ it => it < 0 })
    println("allPos=${allPos}")
}
