// Large #2 (iter6): workflow scheduler with retries and dependencies
enum JobState {
    case pending
    case ready
    case running
    case done
    case failed
}

class Job {
    let name: String
    var deps: [String] = []
    var state: JobState = .pending
    var attempts: Int = 0
    let maxRetries: Int

    init(_ name: String, _ maxRetries: Int) {
        self.name = name
        self.maxRetries = maxRetries
    }

    func dependsOn(_ dep: String) {
        deps.append(dep)
    }
}

class Workflow {
    var jobs: [String: Job] = [:]
    var order: [String] = []

    func add(_ j: Job) {
        jobs[j.name] = j
        order.append(j.name)
    }

    func complete(_ name: String) {
        let j = jobs[name]
        if let jj = j {
            jj.state = .done
        }
    }

    func failOnceThenMaybeReady(_ name: String) {
        let j = jobs[name]
        if let jj = j {
            jj.attempts += 1
            if jj.attempts <= jj.maxRetries {
                jj.state = .ready
            } else {
                jj.state = .failed
            }
        }
    }

    func depsDone(_ j: Job) -> Bool {
        for d in j.deps {
            let dep = jobs[d]
            if let dd = dep {
                if dd.state != .done {
                    return false
                }
            } else {
                return false
            }
        }
        return true
    }

    func refreshReady() {
        for n in order {
            let j = jobs[n]
            if let jj = j {
                if jj.state == .pending && depsDone(jj) {
                    jj.state = .ready
                }
            }
        }
    }

    func nextReady() -> Job? {
        refreshReady()
        for n in order {
            let j = jobs[n]
            if let jj = j {
                if jj.state == .ready {
                    jj.state = .running
                    return jj
                }
            }
        }
        return nil
    }

    func snapshot() -> String {
        var s = ""
        for n in order {
            let j = jobs[n]
            if let jj = j {
                s = s + n + ":" + stateName(jj.state) + "/" + "\(jj.attempts) "
            }
        }
        return s
    }
}

func stateName(_ s: JobState) -> String {
    switch s {
    case .pending:
        return "pending"
    case .ready:
        return "ready"
    case .running:
        return "running"
    case .done:
        return "done"
    case .failed:
        return "failed"
    }
}

let wf = Workflow()
let fetch = Job("fetch", 1)
let parse = Job("parse", 0)
parse.dependsOn("fetch")
let validate = Job("validate", 0)
validate.dependsOn("parse")
let publish = Job("publish", 2)
publish.dependsOn("validate")
wf.add(fetch)
wf.add(parse)
wf.add(validate)
wf.add(publish)

var step = 0
while step < 8 {
    let n = wf.nextReady()
    if let job = n {
        print("run \(job.name) step=\(step)")
        if job.name == "fetch" && job.attempts == 0 {
            wf.failOnceThenMaybeReady(job.name)
        } else {
            wf.complete(job.name)
        }
    } else {
        print("idle step=\(step)")
    }
    print(wf.snapshot())
    step += 1
}
