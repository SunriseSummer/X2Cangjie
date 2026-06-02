package proj_taskrunner

import std.collection.*

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
