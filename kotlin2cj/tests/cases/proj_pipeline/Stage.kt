open class Stage(val stageName: String) {
    var inputCount = 0
    var outputCount = 0

    open fun process(records: MutableList<Record>): MutableList<Record> {
        inputCount = records.size
        outputCount = records.size
        return records
    }

    fun stats(): String = "$stageName: in=$inputCount, out=$outputCount"
}
