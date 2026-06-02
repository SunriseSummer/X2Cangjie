class Sorting {
    fun bubbleSort(arr: ArrayList<Long>): ArrayList<Long> {
        val result = ArrayList<Long>()
        for (v in arr) result.add(v)
        var n = result.size
        var i = 0
        while (i < n - 1) {
            var j = 0
            while (j < n - 1 - i) {
                if (result[j] > result[j + 1]) {
                    val temp = result[j]
                    result[j] = result[j + 1]
                    result[j + 1] = temp
                }
                j++
            }
            i++
        }
        return result
    }

    fun selectionSort(arr: ArrayList<Long>): ArrayList<Long> {
        val result = ArrayList<Long>()
        for (v in arr) result.add(v)
        var n = result.size
        var i = 0
        while (i < n - 1) {
            var minIdx = i
            var j = i + 1
            while (j < n) {
                if (result[j] < result[minIdx]) {
                    minIdx = j
                }
                j++
            }
            if (minIdx != i) {
                val temp = result[i]
                result[i] = result[minIdx]
                result[minIdx] = temp
            }
            i++
        }
        return result
    }

    fun insertionSort(arr: ArrayList<Long>): ArrayList<Long> {
        val result = ArrayList<Long>()
        for (v in arr) result.add(v)
        var i = 1
        while (i < result.size) {
            val key = result[i]
            var j = i - 1
            while (j >= 0 && result[j] > key) {
                result[j + 1] = result[j]
                j--
            }
            result[j + 1] = key
            i++
        }
        return result
    }

    fun mergeSort(arr: ArrayList<Long>): ArrayList<Long> {
        if (arr.size <= 1) return arr
        val mid = arr.size / 2
        val leftArr = ArrayList<Long>()
        val rightArr = ArrayList<Long>()
        var i = 0
        while (i < mid) {
            leftArr.add(arr[i])
            i++
        }
        while (i < arr.size) {
            rightArr.add(arr[i])
            i++
        }
        val sortedLeft = mergeSort(leftArr)
        val sortedRight = mergeSort(rightArr)
        return merge(sortedLeft, sortedRight)
    }

    private fun merge(left: ArrayList<Long>, right: ArrayList<Long>): ArrayList<Long> {
        val result = ArrayList<Long>()
        var i = 0
        var j = 0
        while (i < left.size && j < right.size) {
            if (left[i] <= right[j]) {
                result.add(left[i])
                i++
            } else {
                result.add(right[j])
                j++
            }
        }
        while (i < left.size) {
            result.add(left[i])
            i++
        }
        while (j < right.size) {
            result.add(right[j])
            j++
        }
        return result
    }
}
