package proj_taskrunner

import std.collection.*

class TaskRunner {
    let runnerName: String
    init(runnerName: String) {
        this.runnerName = runnerName
    }
    let queues = ArrayList<TaskQueue>()
    var tasksProcessed = 0
    func addQueue(queue: TaskQueue) {
        queues.add(queue)
    }
    func processNext(): Bool {
        for (q in queues) {
            let task = q.dequeueHighest()
            if (let Some(task) <- task) {
                println("  Runner '${runnerName}' executing: ${task.name}")
                q.markDone(task)
                tasksProcessed += 1
                return true
            }
        }
        return false
    }
    func processAll() {
        println("Runner '${runnerName}' starting...")
        while (processNext()) {}
        println("Runner '${runnerName}' finished. Processed ${tasksProcessed} tasks.")
    }
    func printReport() {
        println("=== Runner Report: ${runnerName} ===")
        println("Tasks processed: ${tasksProcessed}")
        for (q in queues) {
            q.printStatus()
        }
    }
}
