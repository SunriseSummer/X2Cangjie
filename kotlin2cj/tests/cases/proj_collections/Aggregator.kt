package proj_collections

class Aggregator(val numbers: List<Int>) {
    fun stats(): String {
        val sorted = numbers.sorted()
        val min = sorted.first()
        val max = sorted.last()
        val sum = numbers.sum()
        val count = numbers.count()
        return "min=$min max=$max sum=$sum count=$count"
    }

    fun duplicates(): List<Int> {
        val seen = mutableSetOf<Int>()
        val dups = mutableListOf<Int>()
        for (n in numbers) {
            if (seen.contains(n)) {
                if (!dups.contains(n)) dups.add(n)
            }
            seen.add(n)
        }
        return dups
    }

    fun topN(n: Int): List<Int> {
        return numbers.sortedDescending().take(n)
    }
}
