package proj_linkedlist

import std.collection.*

class Node {
    let value: Int64
    var next: ?Node
    init(value: Int64, next: ?Node) {
        this.value = value
        this.next = next
    }
}

class LinkedList {
    var head: ?Node = None
    var size: Int64 = 0
    func append(value: Int64) {
        let newNode = Node(value, None)
        if (head.isNone()) {
            head = newNode
        } else {
            var current = head
            while (current.isSome()) {
                if (current.getOrThrow().next.isNone()) {
                    current.getOrThrow().next = newNode
                    break
                }
                current = current.getOrThrow().next
            }
        }
        size += 1
    }
    func prepend(value: Int64) {
        let newNode = Node(value, head)
        head = newNode
        size += 1
    }
    func removeFirst(): Int64 {
        if (head.isSome()) {
            let value = head.getOrThrow().value
            head = head.getOrThrow().next
            size -= 1
            return value
        }
        return -1
    }
    func toList(): ArrayList<Int64> {
        let result = ArrayList<Int64>()
        var current = head
        while (current.isSome()) {
            result.add(current.getOrThrow().value)
            current = current.getOrThrow().next
        }
        return result
    }
    func reverse() {
        var prev: ?Node = None
        var current = head
        while (current.isSome()) {
            let next = current.getOrThrow().next
            current.getOrThrow().next = prev
            prev = current
            current = next
        }
        head = prev
    }
}

main() {
    let list = LinkedList()
    list.append(1)
    list.append(2)
    list.append(3)
    list.prepend(0)
    println("List: ${list.toList()}")
    println("Size: ${list.size}")
    list.reverse()
    println("Reversed: ${list.toList()}")
    let removed = list.removeFirst()
    println("Removed: ${removed}")
    println("After remove: ${list.toList()}")
}