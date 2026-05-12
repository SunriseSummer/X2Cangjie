// Medium #1: queue + producer/consumer simulation (~80 lines)
class Queue<T> {
    var items: [T] = []

    func enqueue(_ x: T) {
        items.append(x)
    }

    func dequeue() -> T {
        let x = items[0]
        items.remove(at: 0)
        return x
    }

    func size() -> Int {
        return items.count
    }

    func isEmpty() -> Bool {
        return items.count == 0
    }
}

class Task {
    let id: Int
    let cost: Int
    init(id: Int, cost: Int) {
        self.id = id
        self.cost = cost
    }
    func describe() -> String {
        return "task(\(id) cost=\(cost))"
    }
}

class Worker {
    let name: String
    var busyUntil: Int = 0
    var done: Int = 0

    init(name: String) {
        self.name = name
    }

    func accept(task: Task, now: Int) -> Int {
        let start = (busyUntil > now) ? busyUntil : now
        let end = start + task.cost
        busyUntil = end
        done += 1
        return end
    }
}

let queue = Queue<Task>()
for i in 1 ... 8 {
    queue.enqueue(Task(id: i, cost: i * 3))
}
print("queue size = \(queue.size())")

let workers: [Worker] = [Worker(name: "W1"), Worker(name: "W2")]
var now = 0
while !queue.isEmpty() {
    let t = queue.dequeue()
    // pick worker with smallest busyUntil
    var best = workers[0]
    for w in workers {
        if w.busyUntil < best.busyUntil {
            best = w
        }
    }
    let finish = best.accept(task: t, now: now)
    print("\(best.name) -> \(t.describe()) finish=\(finish)")
    now = (now + 1)
}

for w in workers {
    print("\(w.name) done=\(w.done) busyUntil=\(w.busyUntil)")
}
