package proj_pipeline

import std.collection.*

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
