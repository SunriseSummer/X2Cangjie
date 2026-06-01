// Custom iterator pattern with complex data traversal
class TreeNode(val value: Int) {
    val children = ArrayList<TreeNode>()
    fun addChild(v: Int): TreeNode {
        val child = TreeNode(v)
        children.add(child)
        return child
    }
}

fun preorder(node: TreeNode, result: ArrayList<Int>) {
    result.add(node.value)
    for (child in node.children) {
        preorder(child, result)
    }
}

fun postorder(node: TreeNode, result: ArrayList<Int>) {
    for (child in node.children) {
        postorder(child, result)
    }
    result.add(node.value)
}

fun treeDepth(node: TreeNode): Int {
    if (node.children.isEmpty()) return 1
    var maxChildDepth = 0
    for (child in node.children) {
        val d = treeDepth(child)
        if (d > maxChildDepth) maxChildDepth = d
    }
    return 1 + maxChildDepth
}

fun leafCount(node: TreeNode): Int {
    if (node.children.isEmpty()) return 1
    var count = 0
    for (child in node.children) {
        count += leafCount(child)
    }
    return count
}

fun main() {
    // Build a tree:
    //       1
    //      / \
    //     2   3
    //    /|   |
    //   4 5   6
    //         |
    //         7
    val root = TreeNode(1)
    val n2 = root.addChild(2)
    val n3 = root.addChild(3)
    n2.addChild(4)
    n2.addChild(5)
    val n6 = n3.addChild(6)
    n6.addChild(7)

    val pre = ArrayList<Int>()
    preorder(root, pre)
    println("Preorder: ${pre.joinToString(" ")}")

    val post = ArrayList<Int>()
    postorder(root, post)
    println("Postorder: ${post.joinToString(" ")}")

    println("Depth: ${treeDepth(root)}")
    println("Leaves: ${leafCount(root)}")
    println("Sum: ${pre.sum()}")
}
