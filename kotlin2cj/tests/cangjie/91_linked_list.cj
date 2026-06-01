import std.collection.*

class ListNode {
    let value: Int64
    var next: ?ListNode
    init(value: Int64, next: ?ListNode) {
        this.value = value
        this.next = next
    }
}

func buildList(arr: ArrayList<Int64>): ?ListNode {
    if (arr.isEmpty()) {
        return None
    }
    let head = ListNode(arr[0], None)
    var cur = head
    for (i in 1..arr.size) {
        let node = ListNode(arr[i], None)
        cur.next = node
        cur = node
    }
    return head
}

func printList(head: ?ListNode) {
    var cur = head
    let parts = ArrayList<String>()
    while (cur.isSome()) {
        parts.add(cur.getOrThrow().value.toString())
        cur = cur.getOrThrow().next
    }
    println(String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " -> "))
}

func listLength(head: ?ListNode): Int64 {
    var count = 0
    var cur = head
    while (cur.isSome()) {
        count += 1
        cur = cur.getOrThrow().next
    }
    return count
}

func reverseList(head: ?ListNode): ?ListNode {
    var prev: ?ListNode = None
    var cur = head
    while (cur.isSome()) {
        let next = cur.getOrThrow().next
        cur.getOrThrow().next = prev
        prev = cur
        cur = next
    }
    return prev
}

func sumList(head: ?ListNode): Int64 {
    var sum = 0
    var cur = head
    while (cur.isSome()) {
        sum += cur.getOrThrow().value
        cur = cur.getOrThrow().next
    }
    return sum
}

main() {
    let arr = ArrayList([1, 2, 3, 4, 5])
    let head = buildList(arr)
    print("List: ")
    printList(head)
    println("Length: ${listLength(head)}")
    println("Sum: ${sumList(head)}")
    let rev = reverseList(head)
    print("Reversed: ")
    printList(rev)
    let single = ListNode(42, None)
    print("Single: ")
    printList(single)
    println("Single length: ${listLength(single)}")
    let empty: ?ListNode = None
    println("Empty length: ${listLength(empty)}")
    println("Empty sum: ${sumList(empty)}")
}
