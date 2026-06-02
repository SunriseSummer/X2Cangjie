package proj_pipeline

import std.collection.*

class Record <: ToString {
    let id: Int64
    let label: String
    let value: Int64
    init(id: Int64, label: String, value: Int64) {
        this.id = id
        this.label = label
        this.value = value
    }
    func describe(): String {
        return "#${id} ${label}=${value}"
    }
    public func toString(): String {
        return "Record(id=${this.id}, label=${this.label}, value=${this.value})"
    }
}

class DataSource {
    let sourceName: String
    init(sourceName: String) {
        this.sourceName = sourceName
    }
    let records = ArrayList<Record>()
    var nextId = 1
    func add(label: String, value: Int64) {
        records.add(Record(nextId, label, value))
        nextId += 1
    }
    func getAll(): ArrayList<Record> {
        let copy = ArrayList<Record>()
        for (r in records) {
            copy.add(r)
        }
        return copy
    }
    func size(): Int64 {
        return records.size
    }
}
