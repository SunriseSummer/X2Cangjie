fun MutableList<Int>.swapAt(first: Int, second: Int) {
    val temp = this[first]
    this[first] = this[second]
    this[second] = temp
}

fun MutableList<Int>.asNumberString(): String = this.joinToString(", ")

interface SortStrategy {
    val strategyName: String
    fun sort(values: MutableList<Int>): MutableList<Int>
    fun describe(): String
}

data class SortReport(
    val strategyName: String,
    val before: String,
    val after: String,
    val passes: Int,
    val swaps: Int
)

class BubbleSortStrategy(
    val ascending: Boolean = true,
    val label: String = "bubble"
) : SortStrategy {
    override val strategyName: String = if (ascending) {
        "$label-ascending"
    } else {
        "$label-descending"
    }

    var lastPasses = 0
    var lastSwaps = 0

    override fun sort(values: MutableList<Int>): MutableList<Int> {
        val items = mutableListOf<Int>()
        for (value in values) {
            items.add(value)
        }
        lastPasses = 0
        lastSwaps = 0
        if (items.size <= 1) {
            return items
        }
        var end = items.size - 1
        while (end > 0) {
            var swapped = false
            var i = 0
            while (i < end) {
                val shouldSwap = if (ascending) {
                    items[i] > items[i + 1]
                } else {
                    items[i] < items[i + 1]
                }
                if (shouldSwap) {
                    items.swapAt(i, i + 1)
                    swapped = true
                    lastSwaps += 1
                }
                i += 1
            }
            lastPasses += 1
            if (!swapped) {
                break
            }
            end -= 1
        }
        return items
    }

    override fun describe(): String {
        return "Bubble sort compares adjacent values and bubbles extremes toward the edge"
    }
}

class SelectionSortStrategy(
    val ascending: Boolean = true,
    val label: String = "selection"
) : SortStrategy {
    override val strategyName: String = if (ascending) {
        "$label-ascending"
    } else {
        "$label-descending"
    }

    var lastPasses = 0
    var lastSwaps = 0

    override fun sort(values: MutableList<Int>): MutableList<Int> {
        val items = mutableListOf<Int>()
        for (value in values) {
            items.add(value)
        }
        lastPasses = 0
        lastSwaps = 0
        var start = 0
        while (start < items.size) {
            var selected = start
            var i = start + 1
            while (i < items.size) {
                val shouldPick = if (ascending) {
                    items[i] < items[selected]
                } else {
                    items[i] > items[selected]
                }
                if (shouldPick) {
                    selected = i
                }
                i += 1
            }
            if (selected != start) {
                items.swapAt(start, selected)
                lastSwaps += 1
            }
            lastPasses += 1
            start += 1
        }
        return items
    }

    override fun describe(): String {
        return "Selection sort scans the remaining suffix and places one chosen element per pass"
    }
}

class Sorter(initialStrategy: SortStrategy) {
    var strategy: SortStrategy = initialStrategy
    val reports = ArrayList<SortReport>()

    fun changeStrategy(next: SortStrategy) {
        strategy = next
    }

    fun sort(values: MutableList<Int>): MutableList<Int> {
        return strategy.sort(values)
    }

    fun sortAndRecord(values: MutableList<Int>): SortReport {
        val before = values.joinToString(", ")
        val result = strategy.sort(values)
        val after = result.joinToString(", ")
        val report = when (strategy) {
            is BubbleSortStrategy -> {
                val bubble = strategy as BubbleSortStrategy
                SortReport(strategy.strategyName, before, after, bubble.lastPasses, bubble.lastSwaps)
            }
            is SelectionSortStrategy -> {
                val selection = strategy as SelectionSortStrategy
                SortReport(strategy.strategyName, before, after, selection.lastPasses, selection.lastSwaps)
            }
            else -> SortReport(strategy.strategyName, before, after, 0, 0)
        }
        reports.add(report)
        return report
    }

    fun sortMany(listOfLists: MutableList<MutableList<Int>>): MutableList<MutableList<Int>> {
        val result = mutableListOf<MutableList<Int>>()
        for (items in listOfLists) {
            result.add(sort(items))
        }
        return result
    }

    fun reportLines(): MutableList<String> {
        val lines = mutableListOf<String>()
        for (report in reports) {
            lines.add("${report.strategyName}: [${report.before}] -> [${report.after}] passes=${report.passes} swaps=${report.swaps}")
        }
        return lines
    }
}
