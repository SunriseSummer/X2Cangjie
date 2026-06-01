// Linked list with generic-like usage, recursive traversal
class ListNode(val value: Int, var next: ListNode?)

fun buildList(arr: ArrayList<Int>): ListNode? {
    if (arr.isEmpty()) return null
    val head = ListNode(arr[0], null)
    var cur = head
    for (i in 1 until arr.size) {
        val node = ListNode(arr[i], null)
        cur.next = node
        cur = node
    }
    return head
}

fun printList(head: ListNode?) {
    var cur = head
    val parts = ArrayList<String>()
    while (cur != null) {
        parts.add(cur.value.toString())
        cur = cur.next
    }
    println(parts.joinToString(" -> "))
}

fun listLength(head: ListNode?): Int {
    var count = 0
    var cur = head
    while (cur != null) {
        count++
        cur = cur.next
    }
    return count
}

fun reverseList(head: ListNode?): ListNode? {
    var prev: ListNode? = null
    var cur = head
    while (cur != null) {
        val next = cur.next
        cur.next = prev
        prev = cur
        cur = next
    }
    return prev
}

fun sumList(head: ListNode?): Int {
    var sum = 0
    var cur = head
    while (cur != null) {
        sum += cur.value
        cur = cur.next
    }
    return sum
}

fun main() {
    val arr = arrayListOf(1, 2, 3, 4, 5)
    val head = buildList(arr)
    print("List: ")
    printList(head)
    println("Length: ${listLength(head)}")
    println("Sum: ${sumList(head)}")

    val rev = reverseList(head)
    print("Reversed: ")
    printList(rev)

    val single = ListNode(42, null)
    print("Single: ")
    printList(single)
    println("Single length: ${listLength(single)}")

    val empty: ListNode? = null
    println("Empty length: ${listLength(empty)}")
    println("Empty sum: ${sumList(empty)}")
}
