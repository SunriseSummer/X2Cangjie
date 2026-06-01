import std.collection.*

class TreeNode {
    let value: Int64
    init(value: Int64) {
        this.value = value
    }
    let children = ArrayList<TreeNode>()
    func addChild(v: Int64): TreeNode {
        let child = TreeNode(v)
        children.add(child)
        return child
    }
}

func preorder(node: TreeNode, result: ArrayList<Int64>): Unit {
    result.add(node.value)
    for (child in node.children) {
        preorder(child, result)
    }
}

func postorder(node: TreeNode, result: ArrayList<Int64>): Unit {
    for (child in node.children) {
        postorder(child, result)
    }
    result.add(node.value)
}

func treeDepth(node: TreeNode): Int64 {
    if (node.children.isEmpty()) {
        return 1
    }
    var maxChildDepth = 0
    for (child in node.children) {
        let d = treeDepth(child)
        if (d > maxChildDepth) {
            maxChildDepth = d
        }
    }
    return 1 + maxChildDepth
}

func leafCount(node: TreeNode): Int64 {
    if (node.children.isEmpty()) {
        return 1
    }
    var count = 0
    for (child in node.children) {
        count += leafCount(child)
    }
    return count
}

main() {
    let root = TreeNode(1)
    let n2 = root.addChild(2)
    let n3 = root.addChild(3)
    n2.addChild(4)
    n2.addChild(5)
    let n6 = n3.addChild(6)
    n6.addChild(7)
    let pre = ArrayList<Int64>()
    preorder(root, pre)
    println("Preorder: ${String.join(collectArray<String>(pre.iterator().map({e => e.toString()})), delimiter: " ")}")
    let post = ArrayList<Int64>()
    postorder(root, post)
    println("Postorder: ${String.join(collectArray<String>(post.iterator().map({e => e.toString()})), delimiter: " ")}")
    println("Depth: ${treeDepth(root)}")
    println("Leaves: ${leafCount(root)}")
    println("Sum: ${pre.iterator().fold<Int64>(0, {acc, x => acc + x})}")
}
