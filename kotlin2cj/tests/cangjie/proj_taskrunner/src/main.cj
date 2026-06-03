package proj_taskrunner

import std.collection.*

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
