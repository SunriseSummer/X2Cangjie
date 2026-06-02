import std.collection.*

class LRUNode {
    let key: Int64
    var value: Int64
    init(key: Int64, value: Int64) {
        this.key = key
        this.value = value
    }
    var prev: ?LRUNode = None
    var next: ?LRUNode = None
}

class LRUCache {
    let capacity: Int64
    init(capacity: Int64) {
        this.capacity = capacity
    }
    let map = HashMap<Int64, LRUNode>()
    var head: ?LRUNode = None
    var tail: ?LRUNode = None
    var size = 0
    func get(key: Int64): Int64 {
        if (!map.contains(key)) {
            return -1
        }
        let node = map[key]
        moveToFront(node)
        return node.value
    }
    func put(key: Int64, value: Int64) {
        if (map.contains(key)) {
            let node = map[key]
            node.value = value
            moveToFront(node)
            return
        }
        let node = LRUNode(key, value)
        map[key] = node
        addToFront(node)
        size += 1
        if (size > capacity) {
            let removed = removeTail()
            if (let Some(removed) <- removed) {
                map.remove(removed.key)
                size -= 1
            }
        }
    }
    func addToFront(node: LRUNode) {
        node.next = head
        node.prev = None
        let h = head
        if (let Some(h) <- h) {
            h.prev = node
        }
        head = node
        if (tail.isNone()) {
            tail = node
        }
    }
    func removeNode(node: LRUNode) {
        let p = node.prev
        let n = node.next
        if (let Some(p) <- p) {
            p.next = n
        } else {
            head = n
        }
        if (let Some(n) <- n) {
            n.prev = p
        } else {
            tail = p
        }
    }
    func moveToFront(node: LRUNode) {
        removeNode(node)
        addToFront(node)
    }
    func removeTail(): ?LRUNode {
        let t = tail
        if (let Some(t) <- t) {
            removeNode(t)
        }
        return t
    }
    func display(): String {
        let parts = ArrayList<String>()
        var node = head
        while (node.isSome()) {
            let cur = node
            parts.add("${cur.getOrThrow().key}=${cur.getOrThrow().value}")
            node = cur.getOrThrow().next
        }
        return String.join(collectArray<String>(parts.iterator().map({e => e.toString()})), delimiter: " -> ")
    }
}

main() {
    let cache = LRUCache(3)
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
