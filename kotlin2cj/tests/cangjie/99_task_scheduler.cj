import std.collection.*

class Task <: ToString {
    let id: Int64
    let name: String
    let priority: Int64
    let duration: Int64
    init(id: Int64, name: String, priority: Int64, duration: Int64) {
        this.id = id
        this.name = name
        this.priority = priority
        this.duration = duration
    }
    public override func toString(): String {
        return "Task(${name},p=${priority},d=${duration})"
    }
}

class Scheduler {
    let pending = ArrayList<Task>()
    let completed = ArrayList<Task>()
    var time = 0
    func add(task: Task) {
        pending.add(task)
    }
    func run() {
        while (!(pending.isEmpty())) {
            var bestIdx = 0
            for (i in 1..pending.size) {
                let curr = pending[i]
                let best = pending[bestIdx]
                if (curr.priority > best.priority) {
                    bestIdx = i
                } else if ((curr.priority == best.priority) && (curr.id < best.id)) {
                    bestIdx = i
                }
            }
            let task = pending[bestIdx]
            pending.remove(at: bestIdx)
            time += task.duration
            completed.add(task)
            println("  t=${time}: completed ${task.name}")
        }
    }
    func report() {
        println("Total time: ${time}")
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

main() {
    let scheduler = Scheduler()
    scheduler.add(Task(1, "Build", 3, 5))
    scheduler.add(Task(2, "Test", 2, 3))
    scheduler.add(Task(3, "Deploy", 1, 2))
    scheduler.add(Task(4, "Review", 3, 4))
    scheduler.add(Task(5, "Lint", 2, 1))
    println("=== Running scheduler ===")
    scheduler.run()
    println("=== Report ===")
    scheduler.report()
    let s2 = Scheduler()
    s2.add(Task(1, "A", 1, 10))
    s2.add(Task(2, "B", 5, 1))
    println("=== Batch 2 ===")
    s2.run()
    s2.report()
}
