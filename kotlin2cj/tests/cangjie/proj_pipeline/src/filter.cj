package proj_pipeline

import std.collection.*

class FilterStage <: Stage {
    let minValue: Int64
    init(name: String, minValue: Int64) {
        super(name)
        this.minValue = minValue
    }
    public override func process(records: ArrayList<Record>): ArrayList<Record> {
        inputCount = records.size
        let result = ArrayList<Record>()
        for (r in records) {
            if (r.value >= minValue) {
                result.add(r)
            }
        }
        outputCount = result.size
        return result
    }
}

class TransformStage <: Stage {
    let multiplier: Int64
    init(name: String, multiplier: Int64) {
        super(name)
        this.multiplier = multiplier
    }
    public override func process(records: ArrayList<Record>): ArrayList<Record> {
        inputCount = records.size
        let result = ArrayList<Record>()
        for (r in records) {
            result.add(Record(r.id, r.label, r.value * multiplier))
        }
        outputCount = result.size
        return result
    }
}

class SortStage <: Stage {
    init(name: String) {
        super(name)
    }
    public override func process(records: ArrayList<Record>): ArrayList<Record> {
        inputCount = records.size
        let result = ArrayList<Record>()
        for (r in records) {
            result.add(r)
        }
        for (i in 0..result.size) {
            for (j in (i + 1)..result.size) {
                if (result[j].value < result[i].value) {
                    let tmp = result[i]
                    result[i] = result[j]
                    result[j] = tmp
                }
            }
        }
        outputCount = result.size
        return result
    }
}
