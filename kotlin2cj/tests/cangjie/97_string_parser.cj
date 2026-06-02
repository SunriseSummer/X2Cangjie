import std.collection.*

class Record <: ToString {
    let fields: ArrayList<String>
    init(fields: ArrayList<String>) {
        this.fields = fields
    }
    func get(index: Int64): String {
        return fields[index]
    }
    func size(): Int64 {
        return fields.size
    }
    public override func toString(): String {
        return String.join(collectArray<String>(fields.iterator().map({e => e.toString()})), delimiter: "|")
    }
}

func parseLine(line: String): Record {
    let fields = ArrayList<String>()
    var current = ""
    for (ch in line.runes()) {
        if (ch == r',') {
            fields.add(current.trimAscii())
            current = ""
        } else {
            current += ch.toString()
        }
    }
    fields.add(current.trimAscii())
    return Record(fields)
}

func parseCSV(text: String): ArrayList<Record> {
    let records = ArrayList<Record>()
    var line = ""
    for (ch in text.runes()) {
        if (ch == r'\n') {
            if (!(line.isEmpty())) {
                records.add(parseLine(line))
            }
            line = ""
        } else {
            line += ch.toString()
        }
    }
    if (!(line.isEmpty())) {
        records.add(parseLine(line))
    }
    return records
}

main() {
    let csv = "name, age, city\nAlice, 30, Tokyo\nBob, 25, London\nCarol, 35, Paris"
    let records = parseCSV(csv)
    println("Records: ${records.size}")
    for (r in records) {
        println("  ${r}")
    }
    let header = records[0]
    println("Columns: ${header.size()}")
    for (i in 0..header.size()) {
        println("  [${i}] ${header.get(i)}")
    }
    var found = false
    for (i in 1..records.size) {
        if (records[i].get(0) == "Bob") {
            println("Found Bob: age=${records[i].get(1)}, city=${records[i].get(2)}")
            found = true
        }
    }
    if (!found) {
        println("Bob not found")
    }
    println("Data rows: ${records.size - 1}")
}
