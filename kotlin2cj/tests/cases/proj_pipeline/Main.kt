fun main() {
    val source = DataSource("sensors")
    source.add("temp", 25)
    source.add("pressure", 1013)
    source.add("humidity", 60)
    source.add("temp", 5)
    source.add("pressure", 980)
    source.add("humidity", 95)
    source.add("temp", 30)
    source.add("pressure", 1050)

    val pipeline = Pipeline("analysis")
    pipeline.addStage(FilterStage("filter-low", 20))
    pipeline.addStage(TransformStage("scale-x2", 2))
    pipeline.addStage(SortStage("sort-by-value"))

    val results = pipeline.execute(source)

    println()
    println("Results (${results.size} records):")
    for (r in results) {
        println("  ${r.describe()}")
    }

    println()
    pipeline.printStageStats()

    // Second pipeline with different config
    val pipeline2 = Pipeline("summary")
    pipeline2.addStage(FilterStage("big-only", 50))
    pipeline2.addStage(SortStage("sort"))

    println()
    val results2 = pipeline2.execute(source)
    println()
    println("Summary results (${results2.size} records):")
    for (r in results2) {
        println("  ${r.describe()}")
    }
}
