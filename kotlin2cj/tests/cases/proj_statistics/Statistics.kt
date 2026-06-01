class Statistics(val data: MutableList<Int>) {
    fun mean(): Double {
        var sum = 0.0
        for (x in data) {
            sum += x
        }
        return sum / data.size
    }

    fun median(): Double {
        val sorted = data.sorted()
        val n = sorted.size
        if (n % 2 == 0) {
            return (sorted[n / 2 - 1] + sorted[n / 2]).toDouble() / 2.0
        }
        return sorted[n / 2].toDouble()
    }

    fun mode(): Int {
        val freq = mutableMapOf<Int, Int>()
        for (x in data) {
            freq[x] = (freq[x] ?: 0) + 1
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

    fun variance(): Double {
        val m = mean()
        var sum = 0.0
        for (x in data) {
            val diff = x.toDouble() - m
            sum += diff * diff
        }
        return sum / data.size
    }

    fun max(): Int {
        var result = data[0]
        for (i in 1 until data.size) {
            if (data[i] > result) {
                result = data[i]
            }
        }
        return result
    }

    fun min(): Int {
        var result = data[0]
        for (i in 1 until data.size) {
            if (data[i] < result) {
                result = data[i]
            }
        }
        return result
    }

    fun range(): Int = max() - min()
}
