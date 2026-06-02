import std.collection.*

class RangeIterator {
    let start: Int64
    let endExclusive: Int64
    let step: Int64
    init(start: Int64, endExclusive: Int64, step: Int64) {
        this.start = start
        this.endExclusive = endExclusive
        this.step = step
        current = start
    }
    var current: Int64
    func hasNext(): Bool {
        return if (step > 0) {
            current < endExclusive
        } else {
            current > endExclusive
        }
    }
    func next(): Int64 {
        let v = current
        current += step
        return v
    }
}

class FibIterator {
    let limit: Int64
    init(limit: Int64) {
        this.limit = limit
    }
    var a = 0
    var b = 1
    var count = 0
    func hasNext(): Bool {
        return count < limit
    }
    func next(): Int64 {
        let result = a
        let tmp = a + b
        a = b
        b = tmp
        count += 1
        return result
    }
}

func collectRange(start: Int64, end: Int64, step: Int64): ArrayList<Int64> {
    let result = ArrayList<Int64>()
    let iter = RangeIterator(start, end, step)
    while (iter.hasNext()) {
        result.add(iter.next())
    }
    return result
}

func collectFib(n: Int64): ArrayList<Int64> {
    let result = ArrayList<Int64>()
    let iter = FibIterator(n)
    while (iter.hasNext()) {
        result.add(iter.next())
    }
    return result
}

main() {
    let r1 = collectRange(0, 10, 2)
    println(String.join(collectArray<String>(r1.iterator().map({e => e.toString()})), delimiter: " "))
    let r2 = collectRange(10, 0, -3)
    println(String.join(collectArray<String>(r2.iterator().map({e => e.toString()})), delimiter: " "))
    let r3 = collectRange(1, 6, 1)
    println(String.join(collectArray<String>(r3.iterator().map({e => e.toString()})), delimiter: " "))
    let fib = collectFib(10)
    println(String.join(collectArray<String>(fib.iterator().map({e => e.toString()})), delimiter: " "))
    let fib5 = collectFib(5)
    println(String.join(collectArray<String>(fib5.iterator().map({e => e.toString()})), delimiter: " "))
}
