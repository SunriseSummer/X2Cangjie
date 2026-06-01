// Complex data processing pipeline: statistics calculator
fun mean(data: ArrayList<Int>): Double {
    var sum = 0
    for (v in data) sum += v
    return sum.toDouble() / data.size.toDouble()
}

fun median(data: ArrayList<Int>): Double {
    val sorted = ArrayList<Int>()
    for (v in data) sorted.add(v)
    sorted.sort()
    val n = sorted.size
    return if (n % 2 == 0) {
        (sorted[n / 2 - 1] + sorted[n / 2]).toDouble() / 2.0
    } else {
        sorted[n / 2].toDouble()
    }
}

fun variance(data: ArrayList<Int>): Double {
    val m = mean(data)
    var sumSq = 0.0
    for (v in data) {
        val vd = v.toDouble()
        val diff = vd - m
        sumSq += diff * diff
    }
    return sumSq / data.size.toDouble()
}

fun mode(data: ArrayList<Int>): Int {
    val freq = HashMap<Int, Int>()
    for (v in data) {
        freq[v] = (freq[v] ?: 0) + 1
    }
    var maxCount = 0
    var modeVal = data[0]
    for ((v, c) in freq) {
        if (c > maxCount || (c == maxCount && v < modeVal)) {
            maxCount = c
            modeVal = v
        }
    }
    return modeVal
}

fun histogram(data: ArrayList<Int>, buckets: Int): ArrayList<Int> {
    var minVal = data[0]
    var maxVal = data[0]
    for (v in data) {
        if (v < minVal) minVal = v
        if (v > maxVal) maxVal = v
    }
    val range = maxVal - minVal + 1
    val bucketSize = if (range <= buckets) 1 else (range + buckets - 1) / buckets

    val hist = ArrayList<Int>()
    for (i in 0 until buckets) hist.add(0)

    for (v in data) {
        var idx = (v - minVal) / bucketSize
        if (idx >= buckets) idx = buckets - 1
        hist[idx] = hist[idx] + 1
    }
    return hist
}

fun main() {
    val data = arrayListOf(4, 7, 2, 9, 1, 5, 8, 3, 6, 5)

    println("Mean: ${mean(data)}")
    println("Median: ${median(data)}")
    println("Variance: ${variance(data)}")
    println("Mode: ${mode(data)}")

    val hist = histogram(data, 3)
    println("Histogram: ${hist.joinToString(" ")}")

    // Edge case: single element
    val single = arrayListOf(42)
    println("Single mean: ${mean(single)}")
    println("Single median: ${median(single)}")

    // All same
    val same = arrayListOf(5, 5, 5, 5)
    println("Same mean: ${mean(same)}")
    println("Same variance: ${variance(same)}")
}
