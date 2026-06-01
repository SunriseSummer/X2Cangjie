// Nullable chains, elvis operator chains, smart casts
class TreeNode(val value: Int, var left: TreeNode?, var right: TreeNode?)

fun treeDepth(node: TreeNode?): Int {
    if (node == null) return 0
    val leftDepth = treeDepth(node.left)
    val rightDepth = treeDepth(node.right)
    return if (leftDepth > rightDepth) leftDepth + 1 else rightDepth + 1
}

fun treeSum(node: TreeNode?): Int {
    if (node == null) return 0
    return node.value + treeSum(node.left) + treeSum(node.right)
}

fun findNode(node: TreeNode?, target: Int): Boolean {
    if (node == null) return false
    if (node.value == target) return true
    return findNode(node.left, target) || findNode(node.right, target)
}

fun treeMax(node: TreeNode?): Int {
    if (node == null) return -999999
    val leftMax = treeMax(node.left)
    val rightMax = treeMax(node.right)
    var m = node.value
    if (leftMax > m) m = leftMax
    if (rightMax > m) m = rightMax
    return m
}

fun main() {
    //       5
    //      / \
    //     3   8
    //    / \   \
    //   1   4   9
    val root = TreeNode(5,
        TreeNode(3,
            TreeNode(1, null, null),
            TreeNode(4, null, null)),
        TreeNode(8,
            null,
            TreeNode(9, null, null)))

    println("Depth: ${treeDepth(root)}")
    println("Sum: ${treeSum(root)}")
    println("Find 4: ${findNode(root, 4)}")
    println("Find 7: ${findNode(root, 7)}")
    println("Max: ${treeMax(root)}")

    // Null tree
    println("Null depth: ${treeDepth(null)}")
    println("Null sum: ${treeSum(null)}")

    // Single node
    val single = TreeNode(42, null, null)
    println("Single depth: ${treeDepth(single)}")
    println("Single max: ${treeMax(single)}")
}
