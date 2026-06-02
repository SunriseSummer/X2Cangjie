class TreeNode {
    let value: Int64
    var left: ?TreeNode
    var right: ?TreeNode
    init(value: Int64, left: ?TreeNode, right: ?TreeNode) {
        this.value = value
        this.left = left
        this.right = right
    }
}

func treeDepth(node: ?TreeNode): Int64 {
    if (node.isNone()) {
        return 0
    }
    let leftDepth = treeDepth(node.getOrThrow().left)
    let rightDepth = treeDepth(node.getOrThrow().right)
    return if (leftDepth > rightDepth) {
        leftDepth + 1
    } else {
        rightDepth + 1
    }
}

func treeSum(node: ?TreeNode): Int64 {
    if (node.isNone()) {
        return 0
    }
    return (node.getOrThrow().value + treeSum(node.getOrThrow().left)) + treeSum(node.getOrThrow().right)
}

func findNode(node: ?TreeNode, target: Int64): Bool {
    if (node.isNone()) {
        return false
    }
    if (node.getOrThrow().value == target) {
        return true
    }
    return findNode(node.getOrThrow().left, target) || findNode(node.getOrThrow().right, target)
}

func treeMax(node: ?TreeNode): Int64 {
    if (node.isNone()) {
        return -999999
    }
    let leftMax = treeMax(node.getOrThrow().left)
    let rightMax = treeMax(node.getOrThrow().right)
    var m = node.getOrThrow().value
    if (leftMax > m) {
        m = leftMax
    }
    if (rightMax > m) {
        m = rightMax
    }
    return m
}

main() {
    let root = TreeNode(5, TreeNode(3, TreeNode(1, None, None), TreeNode(4, None, None)), TreeNode(8, None, TreeNode(9, None, None)))
    println("Depth: ${treeDepth(root)}")
    println("Sum: ${treeSum(root)}")
    println("Find 4: ${findNode(root, 4)}")
    println("Find 7: ${findNode(root, 7)}")
    println("Max: ${treeMax(root)}")
    println("Null depth: ${treeDepth(None)}")
    println("Null sum: ${treeSum(None)}")
    let single = TreeNode(42, None, None)
    println("Single depth: ${treeDepth(single)}")
    println("Single max: ${treeMax(single)}")
}
