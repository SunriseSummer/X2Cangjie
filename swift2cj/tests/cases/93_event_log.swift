// Medium #1 (iter4): event log with severity & filtering (~120 lines)
enum Severity {
    case debug
    case info
    case warn
    case error
}

class LogEntry {
    let id: Int
    let sev: Severity
    let msg: String
    let ts: Int    // logical timestamp
    init(id: Int, sev: Severity, msg: String, ts: Int) {
        self.id = id
        self.sev = sev
        self.msg = msg
        self.ts = ts
    }
    func sevName() -> String {
        switch sev {
        case .debug: return "DBG"
        case .info:  return "INF"
        case .warn:  return "WRN"
        case .error: return "ERR"
        }
    }
}

func sevLevel(_ s: Severity) -> Int {
    switch s {
    case .debug: return 0
    case .info:  return 1
    case .warn:  return 2
    case .error: return 3
    }
}

class Logger {
    var entries: [LogEntry] = []
    var nextId: Int = 1
    var clock: Int = 0
    var minLevel: Int = 0

    func log(_ sev: Severity, _ msg: String) {
        if sevLevel(sev) < minLevel {
            return
        }
        clock += 1
        let e = LogEntry(id: nextId, sev: sev, msg: msg, ts: clock)
        entries.append(e)
        nextId += 1
    }

    func setMinLevel(_ s: Severity) {
        minLevel = sevLevel(s)
    }

    func countAt(_ s: Severity) -> Int {
        var c = 0
        for e in entries {
            if sevLevel(e.sev) == sevLevel(s) {
                c += 1
            }
        }
        return c
    }

    func dumpAbove(_ s: Severity) {
        let m = sevLevel(s)
        for e in entries {
            if sevLevel(e.sev) >= m {
                print("[\(e.ts)] \(e.sevName()) #\(e.id) \(e.msg)")
            }
        }
    }
}

let logger = Logger()
logger.log(.debug, "tick 1")
logger.log(.info, "system started")
logger.log(.warn, "low memory")
logger.log(.debug, "tick 2")
logger.log(.error, "disk full")

print("total entries = \(logger.entries.count)")
print("DBG count = \(logger.countAt(.debug))")
print("WRN count = \(logger.countAt(.warn))")
print("ERR count = \(logger.countAt(.error))")

print("-- dump above WARN --")
logger.dumpAbove(.warn)

print("-- filter at INFO --")
logger.setMinLevel(.info)
logger.log(.debug, "noisy")    // dropped
logger.log(.info, "still here")
logger.log(.error, "boom")
print("now total = \(logger.entries.count)")
print("-- dump all --")
logger.dumpAbove(.debug)
