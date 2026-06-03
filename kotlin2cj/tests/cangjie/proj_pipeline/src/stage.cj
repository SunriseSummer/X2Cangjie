package proj_pipeline

import std.collection.*

open class Stage {
    let stageName: String
    init(stageName: String) {
        this.stageName = stageName
    }
    var inputCount = 0
    var outputCount = 0
    public open func process(records: ArrayList<Record>): ArrayList<Record> {
        inputCount = records.size
        outputCount = records.size
        return records
    }
    public open func stats(): String {
        return "${stageName}: in=${inputCount}, out=${outputCount}"
    }
}
