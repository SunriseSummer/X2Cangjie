package proj_statistics

import std.collection.*
import std.sort.*

class Statistics {
    let data: ArrayList<Int64>
    init(data: ArrayList<Int64>) {
        this.data = data
    }
    func mean(): Float64 {
        var sum = 0.0
        for (x in data) {
            sum += Float64(x)
        }
        return sum / Float64(data.size)
    }
    func median(): Float64 {
        let sorted = ({ => let _s = collectArrayList(data.iterator()); sort(_s, stable: true); _s })()
        let n = sorted.size
        if ((n % 2) == 0) {
            return Float64((sorted[(n / 2) - 1] + sorted[n / 2])) / 2.0
        }
        return Float64(sorted[n / 2])
    }
    func mode(): Int64 {
        let freq = HashMap<Int64, Int64>()
        for (x in data) {
            freq[x] = (freq.get(x) ?? 0) + 1
        }
        var maxCount = 0
        var result = data[0]
        for ((k, v) in freq) {
            if (v > maxCount) {
                maxCount = v
                result = k
            }
        }
        return result
    }
    func variance(): Float64 {
        let m = mean()
        var sum = 0.0
        for (x in data) {
            let diff = Float64(x) - Float64(m)
            sum += diff * diff
        }
        return sum / Float64(data.size)
    }
    func max(): Int64 {
        var result = data[0]
        for (i in 1..data.size) {
            if (data[i] > result) {
                result = data[i]
            }
        }
        return result
    }
    func min(): Int64 {
        var result = data[0]
        for (i in 1..data.size) {
            if (data[i] < result) {
                result = data[i]
            }
        }
        return result
    }
    func range(): Int64 {
        return max() - min()
    }
}
