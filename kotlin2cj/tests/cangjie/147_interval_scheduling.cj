import std.collection.*

class Interval <: ToString {
    let start: Int64
    let end: Int64
    init(start: Int64, end: Int64) {
        this.start = start
        this.end = end
    }
    public func toString(): String {
        return "Interval(start=${this.start}, end=${this.end})"
    }
}

func maxNonOverlapping(intervals: ArrayList<Interval>): Int64 {
    if (intervals.isEmpty()) {
        return 0
    }
    for (i in 0..intervals.size) {
        for (j in (i + 1)..intervals.size) {
            if (intervals[i].end > intervals[j].end) {
                let tmp = intervals[i]
                intervals[i] = intervals[j]
                intervals[j] = tmp
            }
        }
    }
    var count = 1
    var lastEnd = intervals[0].end
    for (i in 1..intervals.size) {
        if (intervals[i].start >= lastEnd) {
            count += 1
            lastEnd = intervals[i].end
        }
    }
    return count
}

func mergeIntervals(intervals: ArrayList<Interval>): ArrayList<Interval> {
    if (intervals.isEmpty()) {
        return intervals
    }
    for (i in 0..intervals.size) {
        for (j in (i + 1)..intervals.size) {
            if (intervals[i].start > intervals[j].start) {
                let tmp = intervals[i]
                intervals[i] = intervals[j]
                intervals[j] = tmp
            }
        }
    }
    let merged = ArrayList<Interval>()
    var curStart = intervals[0].start
    var curEnd = intervals[0].end
    for (i in 1..intervals.size) {
        if (intervals[i].start <= curEnd) {
            if (intervals[i].end > curEnd) {
                curEnd = intervals[i].end
            }
        } else {
            merged.add(Interval(curStart, curEnd))
            curStart = intervals[i].start
            curEnd = intervals[i].end
        }
    }
    merged.add(Interval(curStart, curEnd))
    return merged
}

main() {
    let intervals = ArrayList([Interval(1, 3), Interval(2, 5), Interval(4, 7), Interval(6, 8), Interval(5, 9)])
    println("Max non-overlapping: ${maxNonOverlapping(intervals)}")
    let toMerge = ArrayList([Interval(1, 3), Interval(2, 6), Interval(8, 10), Interval(15, 18), Interval(9, 11)])
    let merged = mergeIntervals(toMerge)
    for (iv in merged) {
        println("[${iv.start}, ${iv.end}]")
    }
    let allOverlap = ArrayList([Interval(1, 10), Interval(2, 5), Interval(3, 7)])
    let m2 = mergeIntervals(allOverlap)
    for (iv in m2) {
        println("[${iv.start}, ${iv.end}]")
    }
}
