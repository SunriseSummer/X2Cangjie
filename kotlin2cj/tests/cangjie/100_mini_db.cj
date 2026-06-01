import std.collection.*

class Row <: ToString {
    let values: ArrayList<String>
    init(values: ArrayList<String>) {
        this.values = values
    }
    func get(col: Int64): String {
        return values[col]
    }
    func set(col: Int64, v: String) {
        values[col] = v
    }
    public func toString(): String {
        return String.join(collectArray<String>(values.iterator().map({e => e.toString()})), delimiter: " | ")
    }
}

class Table {
    let name: String
    let columns: ArrayList<String>
    init(name: String, columns: ArrayList<String>) {
        this.name = name
        this.columns = columns
    }
    let rows = ArrayList<Row>()
    func insert(vals: ArrayList<String>) {
        rows.add(Row(vals))
    }
    func selectAll(): ArrayList<Row> {
        return rows
    }
    func selectWhere(col: Int64, value: String): ArrayList<Row> {
        let result = ArrayList<Row>()
        for (row in rows) {
            if (row.get(col) == value) {
                result.add(row)
            }
        }
        return result
    }
    func updateWhere(col: Int64, matchVal: String, updateCol: Int64, newVal: String): Int64 {
        var count = 0
        for (row in rows) {
            if (row.get(col) == matchVal) {
                row.set(updateCol, newVal)
                count += 1
            }
        }
        return count
    }
    func deleteWhere(col: Int64, value: String): Int64 {
        let toRemove = ArrayList<Int64>()
        for (i in 0..rows.size) {
            if (rows[i].get(col) == value) {
                toRemove.add(i)
            }
        }
        var count = 0
        for (i in (toRemove.size - 1)..=0 : -1) {
            rows.remove(at: toRemove[i])
            count += 1
        }
        return count
    }
    func count(): Int64 {
        return rows.size
    }
    func print() {
        println("--- ${name} (${String.join(collectArray<String>(columns.iterator().map({e => e.toString()})), delimiter: ", ")}) ---")
        for (row in rows) {
            println("  ${row}")
        }
    }
}

main() {
    let users = Table("users", ArrayList(["id", "name", "role"]))
    users.insert(ArrayList(["1", "Alice", "admin"]))
    users.insert(ArrayList(["2", "Bob", "user"]))
    users.insert(ArrayList(["3", "Carol", "user"]))
    users.insert(ArrayList(["4", "Dave", "admin"]))
    users.insert(ArrayList(["5", "Eve", "user"]))
    users.print()
    println("Total: ${users.count()}")
    let admins = users.selectWhere(2, "admin")
    println("Admins: ${admins.size}")
    for (a in admins) {
        println("  ${a}")
    }
    let updated = users.updateWhere(1, "Bob", 2, "admin")
    println("Updated: ${updated}")
    let newAdmins = users.selectWhere(2, "admin")
    println("Admins after update: ${newAdmins.size}")
    let deleted = users.deleteWhere(1, "Eve")
    println("Deleted: ${deleted}")
    println("Remaining: ${users.count()}")
    users.print()
}
