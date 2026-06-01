class Pipeline(val pipelineName: String) {
    val stages = mutableListOf<Stage>()

    fun addStage(stage: Stage) {
        stages.add(stage)
    }

    fun execute(source: DataSource): MutableList<Record> {
        println("Pipeline '$pipelineName' executing on '${source.sourceName}' (${source.size()} records)")
        var data = source.getAll()
        for (stage in stages) {
            data = stage.process(data)
            println("  After ${stage.stageName}: ${data.size} records")
        }
        return data
    }

    fun printStageStats() {
        println("=== Pipeline '$pipelineName' Stage Stats ===")
        for (s in stages) {
            println("  ${s.stats()}")
        }
    }
}
