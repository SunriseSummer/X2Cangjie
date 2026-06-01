// Mini in-memory database with tables, insert, select, update
class Row(val values: ArrayList<String>) {
    fun get(col: Int): String = values[col]
    fun set(col: Int, v: String) { values[col] = v }
    override fun toString(): String = values.joinToString(" | ")
}

class Table(val name: String, val columns: ArrayList<String>) {
    val rows = ArrayList<Row>()

    fun insert(vals: ArrayList<String>) {
        rows.add(Row(vals))
    }

    fun selectAll(): ArrayList<Row> = rows

    fun selectWhere(col: Int, value: String): ArrayList<Row> {
        val result = ArrayList<Row>()
        for (row in rows) {
            if (row.get(col) == value) {
                result.add(row)
            }
        }
        return result
    }

    fun updateWhere(col: Int, matchVal: String, updateCol: Int, newVal: String): Int {
        var count = 0
        for (row in rows) {
            if (row.get(col) == matchVal) {
                row.set(updateCol, newVal)
                count++
            }
        }
        return count
    }

    fun deleteWhere(col: Int, value: String): Int {
        val toRemove = ArrayList<Int>()
        for (i in 0 until rows.size) {
            if (rows[i].get(col) == value) {
                toRemove.add(i)
            }
        }
        var count = 0
        for (i in toRemove.size - 1 downTo 0) {
            rows.removeAt(toRemove[i])
            count++
        }
        return count
    }

    fun count(): Int = rows.size

    fun print() {
        println("--- $name (${columns.joinToString(", ")}) ---")
        for (row in rows) {
            println("  $row")
        }
    }
}

fun main() {
    val users = Table("users", arrayListOf("id", "name", "role"))
    users.insert(arrayListOf("1", "Alice", "admin"))
    users.insert(arrayListOf("2", "Bob", "user"))
    users.insert(arrayListOf("3", "Carol", "user"))
    users.insert(arrayListOf("4", "Dave", "admin"))
    users.insert(arrayListOf("5", "Eve", "user"))

    users.print()
    println("Total: ${users.count()}")

    val admins = users.selectWhere(2, "admin")
    println("Admins: ${admins.size}")
    for (a in admins) println("  $a")

    val updated = users.updateWhere(1, "Bob", 2, "admin")
    println("Updated: $updated")

    val newAdmins = users.selectWhere(2, "admin")
    println("Admins after update: ${newAdmins.size}")

    val deleted = users.deleteWhere(1, "Eve")
    println("Deleted: $deleted")
    println("Remaining: ${users.count()}")
    users.print()
}
