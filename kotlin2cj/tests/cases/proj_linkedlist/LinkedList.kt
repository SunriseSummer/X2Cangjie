class Node(val value: Int, var next: Node?)

class LinkedList {
    var head: Node? = null
    var size: Int = 0

    fun append(value: Int) {
        val newNode = Node(value, null)
        if (head == null) {
            head = newNode
        } else {
            var current = head
            while (current != null) {
                if (current.next == null) {
                    current.next = newNode
                    break
                }
                current = current.next
            }
        }
        size++
    }

    fun prepend(value: Int) {
        val newNode = Node(value, head)
        head = newNode
        size++
    }

    fun removeFirst(): Int {
        if (head != null) {
            val value = head!!.value
            head = head!!.next
            size--
            return value
        }
        return -1
    }

    fun toList(): MutableList<Int> {
        val result = mutableListOf<Int>()
        var current = head
        while (current != null) {
            result.add(current.value)
            current = current.next
        }
        return result
    }

    fun reverse() {
        var prev: Node? = null
        var current = head
        while (current != null) {
            val next = current.next
            current.next = prev
            prev = current
            current = next
        }
        head = prev
    }
}

fun main() {
    val list = LinkedList()
    list.append(1)
    list.append(2)
    list.append(3)
    list.prepend(0)

    println("List: ${list.toList()}")
    println("Size: ${list.size}")

    list.reverse()
    println("Reversed: ${list.toList()}")

    val removed = list.removeFirst()
    println("Removed: $removed")
    println("After remove: ${list.toList()}")
}
