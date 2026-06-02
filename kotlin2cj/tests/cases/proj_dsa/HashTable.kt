data class HashEntry<V>(val key: String, var value: V)

class HashTable<V>(private val capacity: Int = 7) {
    private val buckets = ArrayList<ArrayList<HashEntry<V>>>()
    private var count: Int = 0

    init {
        var index = 0
        while (index < capacity) {
            buckets.add(ArrayList<HashEntry<V>>())
            index++
        }
    }

    private fun hash(key: String): Int {
        var total = 0
        for (ch in key) {
            total += ch.code
        }
        return total % capacity
    }

    fun put(key: String, value: V): V? {
        val bucket = buckets[hash(key)]
        for (entry in bucket) {
            if (entry.key == key) {
                val oldValue = entry.value
                entry.value = value
                return oldValue
            }
        }
        bucket.add(HashEntry(key, value))
        count++
        return null
    }

    fun get(key: String): V? {
        val bucket = buckets[hash(key)]
        for (entry in bucket) {
            if (entry.key == key) {
                return entry.value
            }
        }
        return null
    }

    fun remove(key: String): V? {
        val bucket = buckets[hash(key)]
        var index = 0
        while (index < bucket.size) {
            if (bucket[index].key == key) {
                val value = bucket[index].value
                bucket.removeAt(index)
                count--
                return value
            }
            index++
        }
        return null
    }

    fun containsKey(key: String): Boolean {
        return get(key) != null
    }

    fun keys(): ArrayList<String> {
        val result = ArrayList<String>()
        for (bucket in buckets) {
            for (entry in bucket) {
                result.add(entry.key)
            }
        }
        return result
    }

    fun values(): ArrayList<V> {
        val result = ArrayList<V>()
        for (bucket in buckets) {
            for (entry in bucket) {
                result.add(entry.value)
            }
        }
        return result
    }

    fun entries(): ArrayList<HashEntry<V>> {
        val result = ArrayList<HashEntry<V>>()
        for (bucket in buckets) {
            for (entry in bucket) {
                result.add(HashEntry(entry.key, entry.value))
            }
        }
        return result
    }

    fun size(): Int {
        return count
    }

    fun isEmpty(): Boolean {
        return count == 0
    }

    fun loadFactor(): Double {
        if (capacity == 0) {
            return 0.0
        }
        return count.toDouble() / capacity.toDouble()
    }

    fun bucketView(index: Int): String {
        if (index < 0 || index >= buckets.size) {
            return "[]"
        }
        val builder = StringBuilder()
        builder.append("[")
        var entryIndex = 0
        while (entryIndex < buckets[index].size) {
            if (entryIndex > 0) {
                builder.append(", ")
            }
            val entry = buckets[index][entryIndex]
            builder.append(entry.key)
            builder.append("=")
            builder.append(entry.value)
            entryIndex++
        }
        builder.append("]")
        return builder.toString()
    }

    fun clear() {
        for (bucket in buckets) {
            bucket.clear()
        }
        count = 0
    }

    override fun toString(): String {
        val builder = StringBuilder()
        builder.append("HashTable{")
        var index = 0
        while (index < buckets.size) {
            if (index > 0) {
                builder.append(", ")
            }
            builder.append(index)
            builder.append(":")
            builder.append(bucketView(index))
            index++
        }
        builder.append("}")
        return builder.toString()
    }
}
