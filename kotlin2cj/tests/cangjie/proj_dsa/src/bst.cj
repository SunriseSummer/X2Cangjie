package proj_dsa

import std.collection.*

class BST <: ToString {
    let values = ArrayList<Int64>()
    let leftChild = ArrayList<Int64>()
    let rightChild = ArrayList<Int64>()
    var rootIdx: Int64 = -1
    func insert(value: Int64): Unit {
        let newIdx = values.size
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
                values.remove(at: values.size - 1)
                leftChild.remove(at: leftChild.size - 1)
                rightChild.remove(at: rightChild.size - 1)
                return
            }
        }
    }
    func contains(value: Int64): Bool {
        var curr = rootIdx
        while (curr >= 0) {
            if (value == values[curr]) {
                return true
            }
            curr = if (value < values[curr]) {
                leftChild[curr]
            } else {
                rightChild[curr]
            }
        }
        return false
    }
    func inorder(): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        inorderHelper(rootIdx, result)
        return result
    }
    func inorderHelper(idx: Int64, result: ArrayList<Int64>): Unit {
        if (idx < 0) {
            return
        }
        inorderHelper(leftChild[idx], result)
        result.add(values[idx])
        inorderHelper(rightChild[idx], result)
    }
    func min(): Int64 {
        var curr = rootIdx
        while (leftChild[curr] >= 0) {
            curr = leftChild[curr]
        }
        return values[curr]
    }
    func max(): Int64 {
        var curr = rootIdx
        while (rightChild[curr] >= 0) {
            curr = rightChild[curr]
        }
        return values[curr]
    }
    func size(): Int64 {
        return values.size
    }
    func height(): Int64 {
        return heightHelper(rootIdx)
    }
    func heightHelper(idx: Int64): Int64 {
        if (idx < 0) {
            return 0
        }
        let lh = heightHelper(leftChild[idx])
        let rh = heightHelper(rightChild[idx])
        return 1 + (if (lh > rh) { lh } else { rh })
    }
    public override func toString(): String {
        return "BST(size=${values.size}, inorder=${inorder()})"
    }
}
