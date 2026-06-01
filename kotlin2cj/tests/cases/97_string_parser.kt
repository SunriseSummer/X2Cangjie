// String parsing: CSV-like parser and formatter
class Record(val fields: ArrayList<String>) {
    fun get(index: Int): String = fields[index]
    fun size(): Int = fields.size
    override fun toString(): String = fields.joinToString("|")
}

fun parseLine(line: String): Record {
    val fields = ArrayList<String>()
    var current = ""
    for (ch in line) {
        if (ch == ',') {
            fields.add(current.trim())
            current = ""
        } else {
            current += ch
        }
    }
    fields.add(current.trim())
    return Record(fields)
}

fun parseCSV(text: String): ArrayList<Record> {
    val records = ArrayList<Record>()
    var line = ""
    for (ch in text) {
        if (ch == '\n') {
            if (line.isNotEmpty()) {
                records.add(parseLine(line))
            }
            line = ""
        } else {
            line += ch
        }
    }
    if (line.isNotEmpty()) {
        records.add(parseLine(line))
    }
    return records
}

fun main() {
    val csv = "name, age, city\nAlice, 30, Tokyo\nBob, 25, London\nCarol, 35, Paris"
    val records = parseCSV(csv)

    println("Records: ${records.size}")
    for (r in records) {
        println("  $r")
    }

    // Access specific fields
    val header = records[0]
    println("Columns: ${header.size()}")
    for (i in 0 until header.size()) {
        println("  [$i] ${header.get(i)}")
    }

    // Find record by name
    var found = false
    for (i in 1 until records.size) {
        if (records[i].get(0) == "Bob") {
            println("Found Bob: age=${records[i].get(1)}, city=${records[i].get(2)}")
            found = true
        }
    }
    if (!found) println("Bob not found")

    // Count non-header records
    println("Data rows: ${records.size - 1}")
}
