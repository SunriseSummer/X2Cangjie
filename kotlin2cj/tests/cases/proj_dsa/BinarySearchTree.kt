class TreeNode(
    var value: Int,
    var left: TreeNode? = null,
    var right: TreeNode? = null
)

class BinarySearchTree {
    private var root: TreeNode? = null
    private var count: Int = 0

    fun insert(value: Int): Boolean {
        val inserted = insertNode(root, value)
        root = inserted.first
        if (inserted.second) {
            count++
        }
        return inserted.second
    }

    fun insertAll(values: ArrayList<Int>) {
        for (value in values) {
            insert(value)
        }
    }

    private fun insertNode(node: TreeNode?, value: Int): Pair<TreeNode?, Boolean> {
        if (node == null) {
            return Pair(TreeNode(value), true)
        }

        return when {
            value < node.value -> {
                val inserted = insertNode(node.left, value)
                node.left = inserted.first
                Pair(node, inserted.second)
            }
            value > node.value -> {
                val inserted = insertNode(node.right, value)
                node.right = inserted.first
                Pair(node, inserted.second)
            }
            else -> Pair(node, false)
        }
    }

    fun search(value: Int): TreeNode? {
        var current = root
        while (current != null) {
            current = when {
                value < current.value -> current.left
                value > current.value -> current.right
                else -> return current
            }
        }
        return null
    }

    fun contains(value: Int): Boolean {
        return search(value) != null
    }

    fun delete(value: Int): Boolean {
        val deleted = deleteNode(root, value)
        root = deleted.first
        if (deleted.second) {
            count--
        }
        return deleted.second
    }

    private fun deleteNode(node: TreeNode?, value: Int): Pair<TreeNode?, Boolean> {
        if (node == null) {
            return Pair(null, false)
        }

        return when {
            value < node.value -> {
                val deleted = deleteNode(node.left, value)
                node.left = deleted.first
                Pair(node, deleted.second)
            }
            value > node.value -> {
                val deleted = deleteNode(node.right, value)
                node.right = deleted.first
                Pair(node, deleted.second)
            }
            else -> {
                if (node.left == null && node.right == null) {
                    Pair(null, true)
                } else if (node.left == null) {
                    Pair(node.right, true)
                } else if (node.right == null) {
                    Pair(node.left, true)
                } else {
                    val successor = findMinNode(node.right)!!
                    node.value = successor.value
                    val deleted = deleteNode(node.right, successor.value)
                    node.right = deleted.first
                    Pair(node, true)
                }
            }
        }
    }

    fun min(): Int? {
        val node = findMinNode(root)
        if (node != null) {
            return node.value
        }
        return null
    }

    fun max(): Int? {
        var current = root
        while (current != null && current.right != null) {
            current = current.right
        }
        if (current != null) {
            return current.value
        }
        return null
    }

    private fun findMinNode(node: TreeNode?): TreeNode? {
        var current = node
        while (current != null && current.left != null) {
            current = current.left
        }
        return current
    }

    fun height(): Int {
        return heightOf(root)
    }

    private fun heightOf(node: TreeNode?): Int {
        if (node == null) {
            return -1
        }
        val leftHeight = heightOf(node.left)
        val rightHeight = heightOf(node.right)
        return maxOf(leftHeight, rightHeight) + 1
    }

    fun inorder(): ArrayList<Int> {
        val result = ArrayList<Int>()
        fillInorder(root, result)
        return result
    }

    private fun fillInorder(node: TreeNode?, result: ArrayList<Int>) {
        if (node == null) {
            return
        }
        fillInorder(node.left, result)
        result.add(node.value)
        fillInorder(node.right, result)
    }

    fun preorder(): ArrayList<Int> {
        val result = ArrayList<Int>()
        fillPreorder(root, result)
        return result
    }

    private fun fillPreorder(node: TreeNode?, result: ArrayList<Int>) {
        if (node == null) {
            return
        }
        result.add(node.value)
        fillPreorder(node.left, result)
        fillPreorder(node.right, result)
    }

    fun postorder(): ArrayList<Int> {
        val result = ArrayList<Int>()
        fillPostorder(root, result)
        return result
    }

    private fun fillPostorder(node: TreeNode?, result: ArrayList<Int>) {
        if (node == null) {
            return
        }
        fillPostorder(node.left, result)
        fillPostorder(node.right, result)
        result.add(node.value)
    }

    fun levelOrder(): ArrayList<Int> {
        val result = ArrayList<Int>()
        if (root == null) {
            return result
        }

        val queue = Queue<TreeNode>()
        queue.enqueue(root!!)
        while (!queue.isEmpty()) {
            val node = queue.dequeue()!!
            result.add(node.value)
            if (node.left != null) {
                queue.enqueue(node.left!!)
            }
            if (node.right != null) {
                queue.enqueue(node.right!!)
            }
        }
        return result
    }

    fun countLeaves(): Int {
        return countLeavesOf(root)
    }

    private fun countLeavesOf(node: TreeNode?): Int {
        if (node == null) {
            return 0
        }
        if (node.left == null && node.right == null) {
            return 1
        }
        return countLeavesOf(node.left) + countLeavesOf(node.right)
    }

    fun sum(): Int {
        return sumOf(root)
    }

    private fun sumOf(node: TreeNode?): Int {
        if (node == null) {
            return 0
        }
        return node.value + sumOf(node.left) + sumOf(node.right)
    }

    fun size(): Int {
        return count
    }

    fun isEmpty(): Boolean {
        return count == 0
    }

    fun clear() {
        root = null
        count = 0
    }

    override fun toString(): String {
        return "BinarySearchTree${inorder()}"
    }
}
