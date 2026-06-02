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

class Pipeline {
    let pipelineName: String
    init(pipelineName: String) {
        this.pipelineName = pipelineName
    }
    let stages = ArrayList<Stage>()
    func addStage(stage: Stage) {
        stages.add(stage)
    }
    func execute(source: DataSource): ArrayList<Record> {
        println("Pipeline '${pipelineName}' executing on '${source.sourceName}' (${source.size()} records)")
        var data = source.getAll()
        for (stage in stages) {
            data = stage.process(data)
            println("  After ${stage.stageName}: ${data.size} records")
        }
        return data
    }
    func printStageStats() {
        println("=== Pipeline '${pipelineName}' Stage Stats ===")
        for (s in stages) {
            println("  ${s.stats()}")
        }
    }
}

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

main() {
    let source = DataSource("sensors")
    source.add("temp", 25)
    source.add("pressure", 1013)
    source.add("humidity", 60)
    source.add("temp", 5)
    source.add("pressure", 980)
    source.add("humidity", 95)
    source.add("temp", 30)
    source.add("pressure", 1050)
    let pipeline = Pipeline("analysis")
    pipeline.addStage(FilterStage("filter-low", 20))
    pipeline.addStage(TransformStage("scale-x2", 2))
    pipeline.addStage(SortStage("sort-by-value"))
    let results = pipeline.execute(source)
    println()
    println("Results (${results.size} records):")
    for (r in results) {
        println("  ${r.describe()}")
    }
    println()
    pipeline.printStageStats()
    let pipeline2 = Pipeline("summary")
    pipeline2.addStage(FilterStage("big-only", 50))
    pipeline2.addStage(SortStage("sort"))
    println()
    let results2 = pipeline2.execute(source)
    println()
    println("Summary results (${results2.size} records):")
    for (r in results2) {
        println("  ${r.describe()}")
    }
}