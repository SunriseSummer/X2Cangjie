// LRU Cache implementation using HashMap + doubly linked list
class LRUNode(val key: Int, var value: Int) {
    var prev: LRUNode? = null
    var next: LRUNode? = null
}

class LRUCache(val capacity: Int) {
    val map = HashMap<Int, LRUNode>()
    var head: LRUNode? = null
    var tail: LRUNode? = null
    var size = 0

    fun get(key: Int): Int {
        if (!map.containsKey(key)) return -1
        val node = map[key]!!
        moveToFront(node)
        return node.value
    }

    fun put(key: Int, value: Int) {
        if (map.containsKey(key)) {
            val node = map[key]!!
            node.value = value
            moveToFront(node)
            return
        }
        val node = LRUNode(key, value)
        map[key] = node
        addToFront(node)
        size++
        if (size > capacity) {
            val removed = removeTail()
            if (removed != null) {
                map.remove(removed.key)
                size--
            }
        }
    }

    private fun addToFront(node: LRUNode) {
        node.next = head
        node.prev = null
        val h = head
        if (h != null) {
            h.prev = node
        }
        head = node
        if (tail == null) {
            tail = node
        }
    }

    private fun removeNode(node: LRUNode) {
        val p = node.prev
        val n = node.next
        if (p != null) {
            p.next = n
        } else {
            head = n
        }
        if (n != null) {
            n.prev = p
        } else {
            tail = p
        }
    }

    private fun moveToFront(node: LRUNode) {
        removeNode(node)
        addToFront(node)
    }

    private fun removeTail(): LRUNode? {
        val t = tail
        if (t != null) {
            removeNode(t)
        }
        return t
    }

    fun display(): String {
        val parts = ArrayList<String>()
        var node = head
        while (node != null) {
            val cur = node
            parts.add("${cur.key}=${cur.value}")
            node = cur.next
        }
        return parts.joinToString(" -> ")
    }
}

fun main() {
    val cache = LRUCache(3)
    cache.put(1, 10)
    cache.put(2, 20)
    cache.put(3, 30)
    println(cache.display())

    println("get(2): ${cache.get(2)}")
    println(cache.display())

    cache.put(4, 40)
    println(cache.display())

    println("get(1): ${cache.get(1)}")
    println("get(3): ${cache.get(3)}")
    println(cache.display())

    cache.put(5, 50)
    println(cache.display())
}
