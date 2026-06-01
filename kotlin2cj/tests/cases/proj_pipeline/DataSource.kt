data class Record(val id: Int, val label: String, val value: Int) {
    fun describe(): String = "#$id $label=$value"
}

class DataSource(val sourceName: String) {
    val records = mutableListOf<Record>()
    var nextId = 1

    fun add(label: String, value: Int) {
        records.add(Record(nextId, label, value))
        nextId++
    }

    fun getAll(): MutableList<Record> {
        val copy = mutableListOf<Record>()
        for (r in records) {
            copy.add(r)
        }
        return copy
    }

    fun size(): Int = records.size
}
