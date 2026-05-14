// Large #2 (iter12): pipeline task simulation with dependencies
class TaskNode {
    let name: String
    let cost: Int
    var deps: [String] = []
    init(_ name: String, _ cost: Int) {
        self.name = name
        self.cost = cost
    }
    func addDep(_ dep: String) { deps.append(dep) }
}

class Pipeline {
    var tasks: [String: TaskNode] = [:]
    func add(_ task: TaskNode) { tasks[task.name] = task }
    func totalCost(_ name: String) -> Int {
        let t = tasks[name]
        if let task = t {
            var total = task.cost
            for dep in task.deps { total += totalCost(dep) }
            return total
        }
        return 0
    }
    func ready(_ done: [String]) -> [String] {
        var out: [String] = []
        for pair in tasks {
            let task = pair.1
            var ok = true
            for dep in task.deps {
                var seen = false
                for d in done { if d == dep { seen = true } }
                if !seen { ok = false }
            }
            if ok { out.append(task.name) }
        }
        return sortStrings(out)
    }
}

func sortStrings(_ xs: [String]) -> [String] {
    var out = xs
    var i = 1
    while i < out.count {
        var j = i
        while j > 0 && out[j] < out[j - 1] {
            let tmp = out[j]
            out[j] = out[j - 1]
            out[j - 1] = tmp
            j -= 1
        }
        i += 1
    }
    return out
}

func join(_ xs: [String]) -> String {
    var s = ""
    var i = 0
    while i < xs.count {
        if i > 0 { s = s + "," }
        s = s + xs[i]
        i += 1
    }
    return s
}

let p = Pipeline()
let build = TaskNode("build", 5)
let test = TaskNode("test", 3)
test.addDep("build")
let pkg = TaskNode("package", 2)
pkg.addDep("test")
p.add(build)
p.add(test)
p.add(pkg)
print("cost=\(p.totalCost("package"))")
let done0: [String] = []
print("ready0=" + join(p.ready(done0)))
print("ready1=" + join(p.ready(["build"])))
