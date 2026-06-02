package proj_collections

import std.collection.*
import std.sort.*

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
