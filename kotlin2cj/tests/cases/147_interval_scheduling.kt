// Interval scheduling / greedy algorithm
data class Interval(val start: Int, val end: Int)

fun maxNonOverlapping(intervals: ArrayList<Interval>): Int {
    if (intervals.isEmpty()) return 0

    // Sort by end time (bubble sort)
    for (i in 0 until intervals.size) {
        for (j in i + 1 until intervals.size) {
            if (intervals[i].end > intervals[j].end) {
                val tmp = intervals[i]
                intervals[i] = intervals[j]
                intervals[j] = tmp
            }
        }
    }

    var count = 1
    var lastEnd = intervals[0].end
    for (i in 1 until intervals.size) {
        if (intervals[i].start >= lastEnd) {
            count++
            lastEnd = intervals[i].end
        }
    }
    return count
}

fun mergeIntervals(intervals: ArrayList<Interval>): ArrayList<Interval> {
    if (intervals.isEmpty()) return intervals

    // Sort by start time
    for (i in 0 until intervals.size) {
        for (j in i + 1 until intervals.size) {
            if (intervals[i].start > intervals[j].start) {
                val tmp = intervals[i]
                intervals[i] = intervals[j]
                intervals[j] = tmp
            }
        }
    }

    val merged = ArrayList<Interval>()
    var curStart = intervals[0].start
    var curEnd = intervals[0].end
    for (i in 1 until intervals.size) {
        if (intervals[i].start <= curEnd) {
            if (intervals[i].end > curEnd) curEnd = intervals[i].end
        } else {
            merged.add(Interval(curStart, curEnd))
            curStart = intervals[i].start
            curEnd = intervals[i].end
        }
    }
    merged.add(Interval(curStart, curEnd))
    return merged
}

fun main() {
    // Max non-overlapping
    val intervals = arrayListOf(
        Interval(1, 3),
        Interval(2, 5),
        Interval(4, 7),
        Interval(6, 8),
        Interval(5, 9)
    )
    println("Max non-overlapping: ${maxNonOverlapping(intervals)}")

    // Merge intervals
    val toMerge = arrayListOf(
        Interval(1, 3),
        Interval(2, 6),
        Interval(8, 10),
        Interval(15, 18),
        Interval(9, 11)
    )
    val merged = mergeIntervals(toMerge)
    for (iv in merged) {
        println("[${iv.start}, ${iv.end}]")
    }

    // Edge case: all overlapping
    val allOverlap = arrayListOf(
        Interval(1, 10),
        Interval(2, 5),
        Interval(3, 7)
    )
    val m2 = mergeIntervals(allOverlap)
    for (iv in m2) {
        println("[${iv.start}, ${iv.end}]")
    }
}
