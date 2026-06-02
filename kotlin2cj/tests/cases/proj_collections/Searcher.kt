package proj_collections

class Searcher(val items: List<Int>) {
    fun firstPositive(): Int = items.indexOfFirst { it > 0 }
    fun lastPositive(): Int = items.indexOfLast { it > 0 }
    fun hasNegative(): Boolean = items.any { it < 0 }
    fun allPositive(): Boolean = items.none { it < 0 }
    fun top3(): List<Int> = items.sorted().reversed().take(3)
    fun skip2(): List<Int> = items.drop(2)
}
