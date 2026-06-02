class HashTable {
    private val capacity: Int = 16
    private val keys = ArrayList<ArrayList<String>>()
    private val vals = ArrayList<ArrayList<Long>>()
    private var count: Int = 0

    init {
        var i = 0
        while (i < capacity) {
            keys.add(ArrayList<String>())
            vals.add(ArrayList<Long>())
            i++
        }
    }

    private fun hash(key: String): Int {
        var h = 0
        var i = 0
        while (i < key.length) {
            h = h * 31 + key[i].code
            i++
        }
        if (h < 0) h = -h
        return h % capacity
    }

    fun put(key: String, value: Long) {
        val idx = hash(key)
        val bucket = keys[idx]
        var i = 0
        while (i < bucket.size) {
            if (bucket[i] == key) {
                vals[idx][i] = value
                return
            }
            i++
        }
        bucket.add(key)
        vals[idx].add(value)
        count++
    }

    fun get(key: String): Long? {
        val idx = hash(key)
        val bucket = keys[idx]
        var i = 0
        while (i < bucket.size) {
            if (bucket[i] == key) {
                return vals[idx][i]
            }
            i++
        }
        return null
    }

    fun hasKey(key: String): Boolean {
        return get(key) != null
    }

    fun remove(key: String): Boolean {
        val idx = hash(key)
        val bucket = keys[idx]
        var i = 0
        while (i < bucket.size) {
            if (bucket[i] == key) {
                bucket.removeAt(i)
                vals[idx].removeAt(i)
                count--
                return true
            }
            i++
        }
        return false
    }

    fun size(): Int {
        return count
    }

    fun allKeys(): ArrayList<String> {
        val result = ArrayList<String>()
        var i = 0
        while (i < capacity) {
            for (key in keys[i]) {
                result.add(key)
            }
            i++
        }
        return result
    }

    override fun toString(): String {
        val builder = StringBuilder()
        builder.append("HashTable{")
        var first = true
        var i = 0
        while (i < capacity) {
            var j = 0
            while (j < keys[i].size) {
                if (!first) builder.append(", ")
                builder.append(keys[i][j])
                builder.append("=")
                builder.append(vals[i][j].toString())
                first = false
                j++
            }
            i++
        }
        builder.append("}")
        return builder.toString()
    }
}
