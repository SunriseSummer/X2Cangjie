package proj_collections

import std.collection.*
import std.sort.*

class Aggregator {
    let numbers: ArrayList<Int64>
    init(numbers: ArrayList<Int64>) {
        this.numbers = numbers
    }
    func stats(): String {
        let sorted = ({ => let _s = collectArrayList(numbers.iterator()); sort(_s, stable: true); _s })()
        let min = sorted[0]
        let max = sorted[sorted.size - 1]
        let sum = numbers.iterator().fold<Int64>(0, {acc, x => acc + x})
        let count = numbers.size
        return "min=${min} max=${max} sum=${sum} count=${count}"
    }
    func duplicates(): ArrayList<Int64> {
        let seen = HashSet<Int64>()
        let dups = ArrayList<Int64>()
        for (n in numbers) {
            if (seen.contains(n)) {
                if (!dups.contains(n)) {
                    dups.add(n)
                }
            }
            seen.add(n)
        }
        return dups
    }
    func topN(n: Int64): ArrayList<Int64> {
        return collectArrayList(({ => let _s = collectArrayList(numbers.iterator()); sort(_s, stable: true, descending: true); _s })().iterator().take(n))
    }
}

class DataProcessor {
    let data: ArrayList<Int64>
    init(data: ArrayList<Int64>) {
        this.data = data
    }
    func doubleAll(): ArrayList<Int64> {
        return collectArrayList(data.iterator().map({ it => it * 2 }))
    }
    func onlyPositive(): ArrayList<Int64> {
        return collectArrayList(data.iterator().filter({ it => it > 0 }))
    }
    func removeNegative(): ArrayList<Int64> {
        return collectArrayList(data.iterator().filter({ _e => !({ it => it < 0 })(_e) }))
    }
    func withIndices(): ArrayList<Int64> {
        return collectArrayList(data.iterator().enumerate().map({ _p => ({ i, v => (i * 10) + v })(_p[0], _p[1]) }))
    }
    func total(): Int64 {
        return data.iterator().fold<Int64>(0, {acc, x => acc + x})
    }
    func productReduce(): Int64 {
        return data.iterator().reduce({ a, b => a * b }).getOrThrow()
    }
}

class Searcher {
    let items: ArrayList<Int64>
    init(items: ArrayList<Int64>) {
        this.items = items
    }
    func firstPositive(): Int64 {
        return ({ => var _i = 0; for (_e in items) { if (({ it => it > 0 })(_e)) { return _i }; _i++ }; return -1 })()
    }
    func lastPositive(): Int64 {
        return ({ => var _r = -1; var _i = 0; for (_e in items) { if (({ it => it > 0 })(_e)) { _r = _i }; _i++ }; return _r })()
    }
    func hasNegative(): Bool {
        return items.iterator().any({ it => it < 0 })
    }
    func allPositive(): Bool {
        return !items.iterator().any({ it => it < 0 })
    }
    func top3(): ArrayList<Int64> {
        return collectArrayList(({ => let _s = collectArrayList(({ => let _s = collectArrayList(items.iterator()); sort(_s, stable: true); _s })().iterator()); _s.reverse(); _s })().iterator().take(3))
    }
    func skip2(): ArrayList<Int64> {
        return collectArrayList(items.iterator().skip(2))
    }
}

main() {
    let proc = DataProcessor(ArrayList([1, -2, 3, -4, 5]))
    println("doubled: ${proc.doubleAll()}")
    println("positive: ${proc.onlyPositive()}")
    println("removeNeg: ${proc.removeNegative()}")
    println("indexed: ${proc.withIndices()}")
    println("total: ${proc.total()}")
    let proc2 = DataProcessor(ArrayList([1, 2, 3, 4]))
    println("product: ${proc2.productReduce()}")
    let s = Searcher(ArrayList([-1, 3, -2, 5, 1]))
    println("firstPos: ${s.firstPositive()}")
    println("lastPos: ${s.lastPositive()}")
    println("hasNeg: ${s.hasNegative()}")
    println("allPos: ${s.allPositive()}")
    println("top3: ${s.top3()}")
    println("skip2: ${s.skip2()}")
    let agg = Aggregator(ArrayList([5, 3, 1, 4, 2, 3, 5]))
    println(agg.stats())
    println("topN: ${agg.topN(3)}")
    println("dups: ${agg.duplicates()}")
}