class FilterStage(name: String, val minValue: Int) : Stage(name) {
    override fun process(records: MutableList<Record>): MutableList<Record> {
        inputCount = records.size
        val result = mutableListOf<Record>()
        for (r in records) {
            if (r.value >= minValue) {
                result.add(r)
            }
        }
        outputCount = result.size
        return result
    }
}

class TransformStage(name: String, val multiplier: Int) : Stage(name) {
    override fun process(records: MutableList<Record>): MutableList<Record> {
        inputCount = records.size
        val result = mutableListOf<Record>()
        for (r in records) {
            result.add(Record(r.id, r.label, r.value * multiplier))
        }
        outputCount = result.size
        return result
    }
}

class SortStage(name: String) : Stage(name) {
    override fun process(records: MutableList<Record>): MutableList<Record> {
        inputCount = records.size
        // Simple bubble sort by value
        val result = mutableListOf<Record>()
        for (r in records) {
            result.add(r)
        }
        for (i in 0 until result.size) {
            for (j in i + 1 until result.size) {
                if (result[j].value < result[i].value) {
                    val tmp = result[i]
                    result[i] = result[j]
                    result[j] = tmp
                }
            }
        }
        outputCount = result.size
        return result
    }
}
