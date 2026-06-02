package proj_todolist

import std.collection.*

class TodoItem <: ToString {
    let id: Int64
    let title: String
    let done: Bool
    init(id: Int64, title: String, done: Bool) {
        this.id = id
        this.title = title
        this.done = done
    }
    public func toString(): String {
        return "TodoItem(id=${this.id}, title=${this.title}, done=${this.done})"
    }
}

class TodoList {
    let items = ArrayList<TodoItem>()
    var nextId = 1
    func addItem(title: String) {
        items.add(TodoItem(nextId, title, false))
        nextId += 1
    }
    func completeItem(id: Int64) {
        for (i in 0..items.size) {
            if (items[i].id == id) {
                items[i] = TodoItem(items[i].id, items[i].title, true)
            }
        }
    }
    func printAll() {
        for (item in items) {
            let status = if (item.done) {
                "[x]"
            } else {
                "[ ]"
            }
            println("${status} #${item.id}: ${item.title}")
        }
    }
    func countDone(): Int64 {
        return items.iterator().filter({ it => it.done }).count()
    }
    func countPending(): Int64 {
        return items.iterator().filter({ it => !it.done }).count()
    }
}
