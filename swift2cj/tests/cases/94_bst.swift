// Medium #2 (iter4): binary search tree with insert / contains / inorder (~120 lines)
class BSTNode {
    var value: Int
    var left: BSTNode? = nil
    var right: BSTNode? = nil
    init(value: Int) {
        self.value = value
    }
}

class BST {
    var root: BSTNode? = nil
    var count: Int = 0

    func insert(_ v: Int) {
        if root == nil {
            root = BSTNode(value: v)
            count += 1
            return
        }
        var cur = root
        while cur != nil {
            let c = cur!
            if v == c.value {
                return
            }
            if v < c.value {
                if c.left == nil {
                    c.left = BSTNode(value: v)
                    count += 1
                    return
                }
                cur = c.left
            } else {
                if c.right == nil {
                    c.right = BSTNode(value: v)
                    count += 1
                    return
                }
                cur = c.right
            }
        }
    }

    func contains(_ v: Int) -> Bool {
        var cur = root
        while cur != nil {
            let c = cur!
            if v == c.value {
                return true
            }
            if v < c.value {
                cur = c.left
            } else {
                cur = c.right
            }
        }
        return false
    }

    func inorder() -> [Int] {
        var out: [Int] = []
        inorderHelper(root, &out)
        return out
    }

    func inorderHelper(_ n: BSTNode?, _ out: inout [Int]) -> Void {
        if n == nil {
            return
        }
        let c = n!
        inorderHelper(c.left, &out)
        out.append(c.value)
        inorderHelper(c.right, &out)
    }

    func height() -> Int {
        return heightHelper(root)
    }

    func heightHelper(_ n: BSTNode?) -> Int {
        if n == nil {
            return 0
        }
        let c = n!
        let l = heightHelper(c.left)
        let r = heightHelper(c.right)
        if l >= r {
            return l + 1
        }
        return r + 1
    }
}

let t = BST()
let xs = [5, 3, 7, 1, 4, 6, 9, 2, 8]
for v in xs {
    t.insert(v)
}
print("size = \(t.count)")
print("contains 4 = \(t.contains(4))")
print("contains 10 = \(t.contains(10))")
print("inorder = \(t.inorder())")
print("height = \(t.height())")

// duplicates ignored
t.insert(5)
t.insert(7)
print("after dup insert size = \(t.count)")

let t2 = BST()
let ys = [10, 5, 15, 2, 8, 12, 20, 1, 3, 11, 13]
for v in ys {
    t2.insert(v)
}
print("t2 size = \(t2.count)")
print("t2 inorder = \(t2.inorder())")
print("t2 height = \(t2.height())")
print("t2 contains 12 = \(t2.contains(12))")
print("t2 contains 99 = \(t2.contains(99))")
