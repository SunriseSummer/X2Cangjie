// Medium #2 (iter2): singly-linked list with insert/remove/reverse (~100 lines)
class Node {
    var value: Int
    var next: Node? = nil
    init(value: Int) {
        self.value = value
    }
}

class LinkedList {
    var head: Node? = nil
    var size: Int = 0

    func pushFront(_ v: Int) {
        let n = Node(value: v)
        n.next = head
        head = n
        size += 1
    }

    func pushBack(_ v: Int) {
        let n = Node(value: v)
        if head == nil {
            head = n
        } else {
            var cur = head!
            while cur.next != nil {
                cur = cur.next!
            }
            cur.next = n
        }
        size += 1
    }

    func popFront() -> Int {
        let v = head!.value
        head = head!.next
        size -= 1
        return v
    }

    func reverse() {
        var prev: Node? = nil
        var cur = head
        while cur != nil {
            let nxt = cur!.next
            cur!.next = prev
            prev = cur
            cur = nxt
        }
        head = prev
    }

    func sum() -> Int {
        var s = 0
        var cur = head
        while cur != nil {
            s += cur!.value
            cur = cur!.next
        }
        return s
    }

    func dump() -> String {
        var out = "["
        var cur = head
        var first = true
        while cur != nil {
            if !first {
                out = out + ", "
            }
            out = out + "\(cur!.value)"
            first = false
            cur = cur!.next
        }
        out = out + "]"
        return out
    }
}

let list = LinkedList()
list.pushBack(1)
list.pushBack(2)
list.pushBack(3)
list.pushFront(0)
print("after init: " + list.dump() + " size=\(list.size) sum=\(list.sum())")

list.reverse()
print("reversed: " + list.dump())

let v = list.popFront()
print("popped \(v): " + list.dump() + " size=\(list.size)")

let list2 = LinkedList()
var i = 1
while i <= 6 {
    list2.pushBack(i * i)
    i += 1
}
print("squares: " + list2.dump() + " sum=\(list2.sum())")
list2.reverse()
print("rev squares: " + list2.dump())
