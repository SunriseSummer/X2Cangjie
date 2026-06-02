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
