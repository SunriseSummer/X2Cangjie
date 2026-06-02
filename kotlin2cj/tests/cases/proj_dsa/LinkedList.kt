class LinkedListNode<T>(var value: T, var next: LinkedListNode<T>? = null)

class LinkedList<T> {
    private var head: LinkedListNode<T>? = null
    private var tail: LinkedListNode<T>? = null
    private var count: Int = 0

    fun addFirst(value: T) {
        val node = LinkedListNode(value, head)
        head = node
        if (tail == null) {
            tail = node
        }
        count++
    }

    fun addLast(value: T) {
        val node = LinkedListNode(value, null)
        if (head == null) {
            head = node
            tail = node
        } else {
            tail!!.next = node
            tail = node
        }
        count++
    }

    fun addAt(index: Int, value: T): Boolean {
        if (index < 0 || index > count) {
            return false
        }

        if (index == 0) {
            addFirst(value)
            return true
        }

        if (index == count) {
            addLast(value)
            return true
        }

        var currentIndex = 0
        var previous = head
        while (previous != null && currentIndex < index - 1) {
            previous = previous.next
            currentIndex++
        }

        if (previous == null) {
            return false
        }

        val node = LinkedListNode(value, previous.next)
        previous.next = node
        count++
        return true
    }

    fun removeFirst(): T? {
        if (head == null) {
            return null
        }

        val value = head!!.value
        head = head!!.next
        if (head == null) {
            tail = null
        }
        count--
        return value
    }

    fun removeLast(): T? {
        if (head == null) {
            return null
        }

        if (head == tail) {
            val value = head!!.value
            head = null
            tail = null
            count = 0
            return value
        }

        var previous = head
        while (previous != null && previous.next != tail) {
            previous = previous.next
        }

        val value = tail!!.value
        tail = previous
        tail!!.next = null
        count--
        return value
    }

    fun remove(value: T): Boolean {
        if (head == null) {
            return false
        }

        if (head!!.value == value) {
            removeFirst()
            return true
        }

        var previous = head
        while (previous != null && previous.next != null) {
            if (previous.next!!.value == value) {
                if (previous.next == tail) {
                    tail = previous
                }
                previous.next = previous.next!!.next
                count--
                return true
            }
            previous = previous.next
        }

        return false
    }

    fun removeAt(index: Int): T? {
        if (index < 0 || index >= count) {
            return null
        }

        if (index == 0) {
            return removeFirst()
        }

        var currentIndex = 0
        var previous = head
        while (previous != null && currentIndex < index - 1) {
            previous = previous.next
            currentIndex++
        }

        if (previous == null || previous.next == null) {
            return null
        }

        val removed = previous.next!!
        previous.next = removed.next
        if (removed == tail) {
            tail = previous
        }
        count--
        return removed.value
    }

    fun find(value: T): LinkedListNode<T>? {
        var current = head
        while (current != null) {
            if (current.value == value) {
                return current
            }
            current = current.next
        }
        return null
    }

    fun contains(value: T): Boolean {
        return find(value) != null
    }

    fun indexOf(value: T): Int {
        var index = 0
        var current = head
        while (current != null) {
            if (current.value == value) {
                return index
            }
            current = current.next
            index++
        }
        return -1
    }

    fun get(index: Int): T? {
        if (index < 0 || index >= count) {
            return null
        }

        var currentIndex = 0
        var current = head
        while (current != null) {
            if (currentIndex == index) {
                return current.value
            }
            current = current.next
            currentIndex++
        }

        return null
    }

    fun set(index: Int, value: T): Boolean {
        if (index < 0 || index >= count) {
            return false
        }

        var currentIndex = 0
        var current = head
        while (current != null) {
            if (currentIndex == index) {
                current.value = value
                return true
            }
            current = current.next
            currentIndex++
        }

        return false
    }

    fun reverse() {
        var previous: LinkedListNode<T>? = null
        var current = head
        tail = head

        while (current != null) {
            val nextNode = current.next
            current.next = previous
            previous = current
            current = nextNode
        }

        head = previous
    }

    fun clear() {
        head = null
        tail = null
        count = 0
    }

    fun size(): Int {
        return count
    }

    fun isEmpty(): Boolean {
        return count == 0
    }

    fun toArrayList(): ArrayList<T> {
        val result = ArrayList<T>()
        var current = head
        while (current != null) {
            result.add(current.value)
            current = current.next
        }
        return result
    }

    fun copy(): LinkedList<T> {
        val copied = LinkedList<T>()
        var current = head
        while (current != null) {
            copied.addLast(current.value)
            current = current.next
        }
        return copied
    }

    fun join(separator: String = " -> "): String {
        val builder = StringBuilder()
        var current = head
        var first = true
        while (current != null) {
            if (!first) {
                builder.append(separator)
            }
            builder.append(current.value)
            first = false
            current = current.next
        }
        return builder.toString()
    }

    override fun toString(): String {
        val builder = StringBuilder()
        builder.append("LinkedList[")
        var current = head
        var first = true
        while (current != null) {
            if (!first) {
                builder.append(", ")
            }
            builder.append(current.value)
            first = false
            current = current.next
        }
        builder.append("]")
        return builder.toString()
    }
}
