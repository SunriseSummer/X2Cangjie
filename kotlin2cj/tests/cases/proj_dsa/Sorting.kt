interface Sorter {
    fun name(): String
    fun sort(list: ArrayList<Int>): ArrayList<Int>
}

abstract class BaseSorter : Sorter {
    protected fun copyInput(list: ArrayList<Int>): ArrayList<Int> {
        val copied = ArrayList<Int>()
        for (value in list) {
            copied.add(value)
        }
        return copied
    }

    protected fun swap(list: ArrayList<Int>, first: Int, second: Int) {
        val temp = list[first]
        list[first] = list[second]
        list[second] = temp
    }

    fun isSorted(list: ArrayList<Int>): Boolean {
        if (list.size <= 1) {
            return true
        }
        var index = 1
        while (index < list.size) {
            if (list[index - 1] > list[index]) {
                return false
            }
            index++
        }
        return true
    }

    override fun toString(): String {
        return name()
    }
}

class BubbleSort : BaseSorter() {
    override fun name(): String {
        return "BubbleSort"
    }

    override fun sort(list: ArrayList<Int>): ArrayList<Int> {
        val result = copyInput(list)
        var end = result.size - 1
        while (end > 0) {
            var index = 0
            var swapped = false
            while (index < end) {
                if (result[index] > result[index + 1]) {
                    swap(result, index, index + 1)
                    swapped = true
                }
                index++
            }
            if (!swapped) {
                break
            }
            end--
        }
        return result
    }
}

class InsertionSort : BaseSorter() {
    override fun name(): String {
        return "InsertionSort"
    }

    override fun sort(list: ArrayList<Int>): ArrayList<Int> {
        val result = copyInput(list)
        var index = 1
        while (index < result.size) {
            val value = result[index]
            var position = index - 1
            while (position >= 0 && result[position] > value) {
                result[position + 1] = result[position]
                position--
            }
            result[position + 1] = value
            index++
        }
        return result
    }
}

class SelectionSort : BaseSorter() {
    override fun name(): String {
        return "SelectionSort"
    }

    override fun sort(list: ArrayList<Int>): ArrayList<Int> {
        val result = copyInput(list)
        var index = 0
        while (index < result.size) {
            var minIndex = index
            var scan = index + 1
            while (scan < result.size) {
                if (result[scan] < result[minIndex]) {
                    minIndex = scan
                }
                scan++
            }
            if (minIndex != index) {
                swap(result, index, minIndex)
            }
            index++
        }
        return result
    }
}

class MergeSort : BaseSorter() {
    override fun name(): String {
        return "MergeSort"
    }

    override fun sort(list: ArrayList<Int>): ArrayList<Int> {
        val copied = copyInput(list)
        return mergeSort(copied)
    }

    private fun mergeSort(list: ArrayList<Int>): ArrayList<Int> {
        if (list.size <= 1) {
            return list
        }

        val middle = list.size / 2
        val left = ArrayList<Int>()
        val right = ArrayList<Int>()

        var index = 0
        while (index < middle) {
            left.add(list[index])
            index++
        }
        while (index < list.size) {
            right.add(list[index])
            index++
        }

        return merge(mergeSort(left), mergeSort(right))
    }

    private fun merge(left: ArrayList<Int>, right: ArrayList<Int>): ArrayList<Int> {
        val result = ArrayList<Int>()
        var leftIndex = 0
        var rightIndex = 0

        while (leftIndex < left.size && rightIndex < right.size) {
            if (left[leftIndex] <= right[rightIndex]) {
                result.add(left[leftIndex])
                leftIndex++
            } else {
                result.add(right[rightIndex])
                rightIndex++
            }
        }

        while (leftIndex < left.size) {
            result.add(left[leftIndex])
            leftIndex++
        }

        while (rightIndex < right.size) {
            result.add(right[rightIndex])
            rightIndex++
        }

        return result
    }
}

class QuickSort : BaseSorter() {
    override fun name(): String {
        return "QuickSort"
    }

    override fun sort(list: ArrayList<Int>): ArrayList<Int> {
        val result = copyInput(list)
        quickSort(result, 0, result.size - 1)
        return result
    }

    private fun quickSort(list: ArrayList<Int>, low: Int, high: Int) {
        if (low >= high) {
            return
        }
        val pivotIndex = partition(list, low, high)
        quickSort(list, low, pivotIndex - 1)
        quickSort(list, pivotIndex + 1, high)
    }

    private fun partition(list: ArrayList<Int>, low: Int, high: Int): Int {
        val pivot = list[high]
        var smaller = low
        var scan = low
        while (scan < high) {
            if (list[scan] <= pivot) {
                swap(list, smaller, scan)
                smaller++
            }
            scan++
        }
        swap(list, smaller, high)
        return smaller
    }
}
