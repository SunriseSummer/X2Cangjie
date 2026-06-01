import std.collection.*

class Counter {
    var count = 0
    func inc() {
        count += 1
    }
    func add(n: Int64) {
        count += n
    }
}

main() {
    let c = Counter()
    for (_ in 0..5) {
        c.inc()
    }
    c.add(10)
    println("count=${c.count}")
    let nums = collectArrayList((1..=10))
    let evens = collectArrayList(nums.iterator().filter({ it => (it % 2) == 0 }))
    println("evens=${String.join(collectArray<String>(evens.iterator().map({e => e.toString()})), delimiter: ",")}")
    println("product=${nums.iterator().fold<Int64>(1, { acc, n => acc * n })}")
}
