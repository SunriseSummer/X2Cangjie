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
