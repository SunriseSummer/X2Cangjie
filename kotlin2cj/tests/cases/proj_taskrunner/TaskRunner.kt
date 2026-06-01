class TaskRunner(val runnerName: String) {
    val queues = mutableListOf<TaskQueue>()
    var tasksProcessed = 0

    fun addQueue(queue: TaskQueue) {
        queues.add(queue)
    }

    fun processNext(): Boolean {
        for (q in queues) {
            val task = q.dequeueHighest()
            if (task != null) {
                println("  Runner '$runnerName' executing: ${task.name}")
                q.markDone(task)
                tasksProcessed++
                return true
            }
        }
        return false
    }

    fun processAll() {
        println("Runner '$runnerName' starting...")
        while (processNext()) {
            // keep processing
        }
        println("Runner '$runnerName' finished. Processed $tasksProcessed tasks.")
    }

    fun printReport() {
        println("=== Runner Report: $runnerName ===")
        println("Tasks processed: $tasksProcessed")
        for (q in queues) {
            q.printStatus()
        }
    }
}
