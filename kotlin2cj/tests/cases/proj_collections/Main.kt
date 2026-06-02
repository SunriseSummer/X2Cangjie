package proj_collections

fun main() {
    // DataProcessor
    val proc = DataProcessor(listOf(1, -2, 3, -4, 5))
    println("doubled: ${proc.doubleAll()}")
    println("positive: ${proc.onlyPositive()}")
    println("removeNeg: ${proc.removeNegative()}")
    println("indexed: ${proc.withIndices()}")
    println("total: ${proc.total()}")

    val proc2 = DataProcessor(listOf(1, 2, 3, 4))
    println("product: ${proc2.productReduce()}")

    // Searcher
    val s = Searcher(listOf(-1, 3, -2, 5, 1))
    println("firstPos: ${s.firstPositive()}")
    println("lastPos: ${s.lastPositive()}")
    println("hasNeg: ${s.hasNegative()}")
    println("allPos: ${s.allPositive()}")
    println("top3: ${s.top3()}")
    println("skip2: ${s.skip2()}")

    // Aggregator
    val agg = Aggregator(listOf(5, 3, 1, 4, 2, 3, 5))
    println(agg.stats())
    println("topN: ${agg.topN(3)}")
    println("dups: ${agg.duplicates()}")
}
