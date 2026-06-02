package proj_taskrunner

import std.collection.*

class Task <: ToString {
    let id: Int64
    let name: String
    let priority: Int64
    init(id: Int64, name: String, priority: Int64) {
        this.id = id
        this.name = name
        this.priority = priority
    }
    var completed: Bool = false
    func complete() {
        completed = true
    }
    func describe(): String {
        let status = if (completed) {
            "DONE"
        } else {
            "TODO"
        }
        return "[${status}] #${id} ${name} (pri=${priority})"
    }
    public func toString(): String {
        return "Task(id=${this.id}, name=${this.name}, priority=${this.priority})"
    }
}

class TaskQueue {
    let name: String
    init(name: String) {
        this.name = name
    }
    let pending = ArrayList<Task>()
    let done = ArrayList<Task>()
    func enqueue(task: Task) {
        pending.add(task)
    }
    func dequeueHighest(): ?Task {
        if (pending.isEmpty()) {
            return None
        }
        var bestIdx = 0
        for (i in 1..pending.size) {
            if (pending[i].priority > pending[bestIdx].priority) {
                bestIdx = i
            }
        }
        let task = pending[bestIdx]
        pending.remove(at: bestIdx)
        return task
    }
    func markDone(task: Task) {
        task.complete()
        done.add(task)
    }
    func pendingCount(): Int64 {
        return pending.size
    }
    func doneCount(): Int64 {
        return done.size
    }
    func printStatus() {
        println("Queue '${name}': ${pendingCount()} pending, ${doneCount()} done")
        if (!(pending.isEmpty())) {
            println("  Pending:")
            for (t in pending) {
                println("    ${t.describe()}")
            }
        }
        if (!(done.isEmpty())) {
            println("  Done:")
            for (t in done) {
                println("    ${t.describe()}")
            }
        }
    }
}

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

main() {
    let q1 = TaskQueue("build")
    q1.enqueue(Task(1, "compile", 3))
    q1.enqueue(Task(2, "lint", 1))
    q1.enqueue(Task(3, "test", 2))
    q1.enqueue(Task(4, "package", 4))
    let q2 = TaskQueue("deploy")
    q2.enqueue(Task(5, "upload", 2))
    q2.enqueue(Task(6, "verify", 3))
    q2.enqueue(Task(7, "notify", 1))
    println("Initial state:")
    q1.printStatus()
    q2.printStatus()
    println()
    let runner = TaskRunner("CI")
    runner.addQueue(q1)
    runner.addQueue(q2)
    runner.processAll()
    println()
    runner.printReport()
}