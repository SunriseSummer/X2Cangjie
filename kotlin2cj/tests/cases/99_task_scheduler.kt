// Task scheduler simulation with priority and dependencies
data class Task(val id: Int, val name: String, val priority: Int, val duration: Int) {
    override fun toString(): String = "Task($name,p=$priority,d=$duration)"
}

class Scheduler {
    val pending = ArrayList<Task>()
    val completed = ArrayList<Task>()
    var time = 0

    fun add(task: Task) {
        pending.add(task)
    }

    fun run() {
        // Sort by priority (higher first), then by id
        while (pending.isNotEmpty()) {
            var bestIdx = 0
            for (i in 1 until pending.size) {
                val curr = pending[i]
                val best = pending[bestIdx]
                if (curr.priority > best.priority) {
                    bestIdx = i
                } else if (curr.priority == best.priority && curr.id < best.id) {
                    bestIdx = i
                }
            }
            val task = pending[bestIdx]
            pending.removeAt(bestIdx)
            time += task.duration
            completed.add(task)
            println("  t=$time: completed ${task.name}")
        }
    }

    fun report() {
        println("Total time: $time")
        println("Tasks completed: ${completed.size}")
        var totalWait = 0
        var t = 0
        for (task in completed) {
            t += task.duration
            totalWait += t
        }
        println("Avg completion time: ${totalWait / completed.size}")
    }
}

fun main() {
    val scheduler = Scheduler()
    scheduler.add(Task(1, "Build", 3, 5))
    scheduler.add(Task(2, "Test", 2, 3))
    scheduler.add(Task(3, "Deploy", 1, 2))
    scheduler.add(Task(4, "Review", 3, 4))
    scheduler.add(Task(5, "Lint", 2, 1))

    println("=== Running scheduler ===")
    scheduler.run()
    println("=== Report ===")
    scheduler.report()

    // Second batch
    val s2 = Scheduler()
    s2.add(Task(1, "A", 1, 10))
    s2.add(Task(2, "B", 5, 1))
    println("=== Batch 2 ===")
    s2.run()
    s2.report()
}
