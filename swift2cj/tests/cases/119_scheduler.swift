// Large #1 (iter7): meeting room scheduler with conflict search
class Meeting {
    let title: String
    let start: Int
    let end: Int
    init(_ title: String, _ start: Int, _ end: Int) {
        self.title = title
        self.start = start
        self.end = end
    }
    func overlaps(_ other: Meeting) -> Bool {
        return start < other.end && other.start < end
    }
    func show() -> String {
        return title + "(" + "\(start)" + "-" + "\(end)" + ")"
    }
}

class Room {
    let name: String
    var meetings: [Meeting] = []
    init(_ name: String) {
        self.name = name
    }
    func canPlace(_ m: Meeting) -> Bool {
        for x in meetings {
            if x.overlaps(m) {
                return false
            }
        }
        return true
    }
    func add(_ m: Meeting) -> Bool {
        if !canPlace(m) {
            return false
        }
        var i = 0
        while i < meetings.count && meetings[i].start < m.start {
            i += 1
        }
        meetings.insert(m, at: i)
        return true
    }
    func timeline() -> String {
        var s = name + ":"
        for m in meetings {
            s = s + " " + m.show()
        }
        return s
    }
}

class Scheduler {
    var rooms: [Room] = []
    func addRoom(_ name: String) {
        rooms.append(Room(name))
    }
    func schedule(_ m: Meeting) -> String {
        for r in rooms {
            if r.add(m) {
                return r.name
            }
        }
        return "rejected"
    }
    func report() {
        for r in rooms {
            print(r.timeline())
        }
    }
}

let s = Scheduler()
s.addRoom("alpha")
s.addRoom("beta")
let meetings = [
    Meeting("standup", 9, 10),
    Meeting("design", 9, 11),
    Meeting("retro", 10, 12),
    Meeting("planning", 11, 13),
    Meeting("demo", 9, 12),
    Meeting("sync", 13, 14)
]
for m in meetings {
    print("schedule " + m.show() + " -> " + s.schedule(m))
}
s.report()
