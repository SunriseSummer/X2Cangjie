package proj_dsa

import std.collection.*

class Sorting {
    func bubbleSort(arr: ArrayList<Int64>): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        for (v in arr) {
            result.add(v)
        }
        var n = result.size
        var i = 0
        while (i < (n - 1)) {
            var j = 0
            while (j < ((n - 1) - i)) {
                if (result[j] > result[j + 1]) {
                    let temp = result[j]
                    result[j] = result[j + 1]
                    result[j + 1] = temp
                }
                j += 1
            }
            i += 1
        }
        return result
    }
    func selectionSort(arr: ArrayList<Int64>): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        for (v in arr) {
            result.add(v)
        }
        var n = result.size
        var i = 0
        while (i < (n - 1)) {
            var minIdx = i
            var j = i + 1
            while (j < n) {
                if (result[j] < result[minIdx]) {
                    minIdx = j
                }
                j += 1
            }
            if (minIdx != i) {
                let temp = result[i]
                result[i] = result[minIdx]
                result[minIdx] = temp
            }
            i += 1
        }
        return result
    }
    func insertionSort(arr: ArrayList<Int64>): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        for (v in arr) {
            result.add(v)
        }
        var i = 1
        while (i < result.size) {
            let key = result[i]
            var j = i - 1
            while ((j >= 0) && (result[j] > key)) {
                result[j + 1] = result[j]
                j -= 1
            }
            result[j + 1] = key
            i += 1
        }
        return result
    }
    func mergeSort(arr: ArrayList<Int64>): ArrayList<Int64> {
        if (arr.size <= 1) {
            return arr
        }
        let mid = arr.size / 2
        let leftArr = ArrayList<Int64>()
        let rightArr = ArrayList<Int64>()
        var i = 0
        while (i < mid) {
            leftArr.add(arr[i])
            i += 1
        }
        while (i < arr.size) {
            rightArr.add(arr[i])
            i += 1
        }
        let sortedLeft = mergeSort(leftArr)
        let sortedRight = mergeSort(rightArr)
        return merge(sortedLeft, sortedRight)
    }
    func merge(left: ArrayList<Int64>, right: ArrayList<Int64>): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        var i = 0
        var j = 0
        while ((i < left.size) && (j < right.size)) {
            if (left[i] <= right[j]) {
                result.add(left[i])
                i += 1
            } else {
                result.add(right[j])
                j += 1
            }
        }
        while (i < left.size) {
            result.add(left[i])
            i += 1
        }
        while (j < right.size) {
            result.add(right[j])
            j += 1
        }
        return result
    }
}
