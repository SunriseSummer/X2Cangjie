package proj_dsa

import std.collection.*

class HashTable <: ToString {
    init() {
        var i = 0
        while (i < capacity) {
            keys.add(ArrayList<String>())
            vals.add(ArrayList<Int64>())
            i += 1
        }
    }
    let capacity: Int64 = 16
    let keys = ArrayList<ArrayList<String>>()
    let vals = ArrayList<ArrayList<Int64>>()
    var count: Int64 = 0
    func hash(key: String): Int64 {
        var h = 0
        var i = 0
        while (i < key.size) {
            h = (h * 31) + Int64(UInt32(key.toRuneArray()[i]))
            i += 1
        }
        if (h < 0) {
            h = -h
        }
        return h % capacity
    }
    func put(key: String, value: Int64) {
        let idx = hash(key)
        let bucket = keys[idx]
        var i = 0
        while (i < bucket.size) {
            if (bucket[i] == key) {
                vals[idx][i] = value
                return
            }
            i += 1
        }
        bucket.add(key)
        vals[idx].add(value)
        count += 1
    }
    func get(key: String): ?Int64 {
        let idx = hash(key)
        let bucket = keys[idx]
        var i = 0
        while (i < bucket.size) {
            if (bucket[i] == key) {
                return vals[idx][i]
            }
            i += 1
        }
        return None
    }
    func hasKey(key: String): Bool {
        return get(key).isSome()
    }
    func remove(key: String): Bool {
        let idx = hash(key)
        let bucket = keys[idx]
        var i = 0
        while (i < bucket.size) {
            if (bucket[i] == key) {
                bucket.remove(at: i)
                vals[idx].remove(at: i)
                count -= 1
                return true
            }
            i += 1
        }
        return false
    }
    func size(): Int64 {
        return count
    }
    func allKeys(): ArrayList<String> {
        let result = ArrayList<String>()
        var i = 0
        while (i < capacity) {
            for (key in keys[i]) {
                result.add(key)
            }
            i += 1
        }
        return result
    }
    public override func toString(): String {
        let builder = StringBuilder()
        builder.append("HashTable{")
        var first = true
        var i = 0
        while (i < capacity) {
            var j = 0
            while (j < keys[i].size) {
                if (!first) {
                    builder.append(", ")
                }
                builder.append(keys[i][j])
                builder.append("=")
                builder.append(vals[i][j].toString())
                first = false
                j += 1
            }
            i += 1
        }
        builder.append("}")
        return builder.toString()
    }
}
