class BST {
    private val values = ArrayList<Long>()
    private val leftChild = ArrayList<Int>()
    private val rightChild = ArrayList<Int>()
    private var rootIdx: Int = -1

    fun insert(value: Long) {
        val newIdx = values.size
        values.add(value)
        leftChild.add(-1)
        rightChild.add(-1)
        if (rootIdx < 0) {
            rootIdx = newIdx
            return
        }
        var curr = rootIdx
        while (true) {
            if (value < values[curr]) {
                if (leftChild[curr] < 0) {
                    leftChild[curr] = newIdx
                    return
                }
                curr = leftChild[curr]
            } else if (value > values[curr]) {
                if (rightChild[curr] < 0) {
                    rightChild[curr] = newIdx
                    return
                }
                curr = rightChild[curr]
            } else {
                // duplicate, don't insert
                values.removeAt(values.size - 1)
                leftChild.removeAt(leftChild.size - 1)
                rightChild.removeAt(rightChild.size - 1)
                return
            }
        }
    }

    fun contains(value: Long): Boolean {
        var curr = rootIdx
        while (curr >= 0) {
            if (value == values[curr]) return true
            curr = if (value < values[curr]) leftChild[curr] else rightChild[curr]
        }
        return false
    }

    fun inorder(): ArrayList<Long> {
        val result = ArrayList<Long>()
        inorderHelper(rootIdx, result)
        return result
    }

    private fun inorderHelper(idx: Int, result: ArrayList<Long>) {
        if (idx < 0) return
        inorderHelper(leftChild[idx], result)
        result.add(values[idx])
        inorderHelper(rightChild[idx], result)
    }

    fun min(): Long {
        var curr = rootIdx
        while (leftChild[curr] >= 0) {
            curr = leftChild[curr]
        }
        return values[curr]
    }

    fun max(): Long {
        var curr = rootIdx
        while (rightChild[curr] >= 0) {
            curr = rightChild[curr]
        }
        return values[curr]
    }

    fun size(): Int {
        return values.size
    }

    fun height(): Int {
        return heightHelper(rootIdx)
    }

    private fun heightHelper(idx: Int): Int {
        if (idx < 0) return 0
        val lh = heightHelper(leftChild[idx])
        val rh = heightHelper(rightChild[idx])
        return 1 + maxOf(lh, rh)
    }

    override fun toString(): String {
        return "BST(size=${values.size}, inorder=${inorder()})"
    }
}
