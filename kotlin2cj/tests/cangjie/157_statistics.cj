import std.collection.*
import std.sort.*

func mean(data: ArrayList<Int64>): Float64 {
    var sum = 0
    for (v in data) {
        sum += v
    }
    return Float64(sum) / Float64(data.size)
}

func median(data: ArrayList<Int64>): Float64 {
    let sorted = ArrayList<Int64>()
    for (v in data) {
        sorted.add(v)
    }
    sort(sorted, stable: true)
    let n = sorted.size
    return if ((n % 2) == 0) {
        Float64((sorted[(n / 2) - 1] + sorted[n / 2])) / 2.0
    } else {
        Float64(sorted[n / 2])
    }
}

func variance(data: ArrayList<Int64>): Float64 {
    let m = mean(data)
    var sumSq = 0.0
    for (v in data) {
        let vd = Float64(v)
        let diff = vd - Float64(m)
        sumSq += diff * diff
    }
    return sumSq / Float64(data.size)
}

func mode(data: ArrayList<Int64>): Int64 {
    let freq = HashMap<Int64, Int64>()
    for (v in data) {
        freq[v] = (freq.get(v) ?? 0) + 1
    }
    var maxCount = 0
    var modeVal = data[0]
    for ((v, c) in freq) {
        if ((c > maxCount) || ((c == maxCount) && (v < modeVal))) {
            maxCount = c
            modeVal = v
        }
    }
    return modeVal
}

func histogram(data: ArrayList<Int64>, buckets: Int64): ArrayList<Int64> {
    var minVal = data[0]
    var maxVal = data[0]
    for (v in data) {
        if (v < minVal) {
            minVal = v
        }
        if (v > maxVal) {
            maxVal = v
        }
    }
    let range = (maxVal - minVal) + 1
    let bucketSize = if (range <= buckets) {
        1
    } else {
        ((range + buckets) - 1) / buckets
    }
    let hist = ArrayList<Int64>()
    for (i in 0..buckets) {
        hist.add(0)
    }
    for (v in data) {
        var idx = (v - minVal) / bucketSize
        if (idx >= buckets) {
            idx = buckets - 1
        }
        hist[idx] = hist[idx] + 1
    }
    return hist
}

main() {
    let data = ArrayList([4, 7, 2, 9, 1, 5, 8, 3, 6, 5])
    println("Mean: ${mean(data)}")
    println("Median: ${median(data)}")
    println("Variance: ${variance(data)}")
    println("Mode: ${mode(data)}")
    let hist = histogram(data, 3)
    println("Histogram: ${String.join(collectArray<String>(hist.iterator().map({e => e.toString()})), delimiter: " ")}")
    let single = ArrayList([42])
    println("Single mean: ${mean(single)}")
    println("Single median: ${median(single)}")
    let same = ArrayList([5, 5, 5, 5])
    println("Same mean: ${mean(same)}")
    println("Same variance: ${variance(same)}")
}
