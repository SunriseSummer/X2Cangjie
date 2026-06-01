class TaskQueue(val name: String) {
    val pending = mutableListOf<Task>()
    val done = mutableListOf<Task>()

    fun enqueue(task: Task) {
        pending.add(task)
    }

    fun dequeueHighest(): Task? {
        if (pending.isEmpty()) return null
        var bestIdx = 0
        for (i in 1 until pending.size) {
            if (pending[i].priority > pending[bestIdx].priority) {
                bestIdx = i
            }
        }
        val task = pending[bestIdx]
        pending.removeAt(bestIdx)
        return task
    }

    fun markDone(task: Task) {
        task.complete()
        done.add(task)
    }

    fun pendingCount(): Int = pending.size
    fun doneCount(): Int = done.size

    fun printStatus() {
        println("Queue '$name': ${pendingCount()} pending, ${doneCount()} done")
        if (pending.isNotEmpty()) {
            println("  Pending:")
            for (t in pending) {
                println("    ${t.describe()}")
            }
        }
        if (done.isNotEmpty()) {
            println("  Done:")
            for (t in done) {
                println("    ${t.describe()}")
            }
        }
    }
}
