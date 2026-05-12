// Large #2 (iter10): ticket queue with priority and status transitions
enum TicketStatus {
    case open
    case assigned
    case closed
}

class Ticket {
    let id: String
    let priority: Int
    var status: TicketStatus = .open
    var assignee: String = ""
    init(_ id: String, _ priority: Int) {
        self.id = id
        self.priority = priority
    }
    func label() -> String { return id + ":p\(priority):" + statusName(status) + ":" + assignee }
}

func statusName(_ s: TicketStatus) -> String {
    switch s {
    case .open: return "open"
    case .assigned: return "assigned"
    case .closed: return "closed"
    }
}

class TicketQueue {
    var tickets: [Ticket] = []
    func add(_ t: Ticket) { tickets.append(t) }
    func nextOpen() -> Ticket? {
        var best = -1
        var i = 0
        while i < tickets.count {
            if tickets[i].status == .open {
                if best < 0 || tickets[i].priority > tickets[best].priority { best = i }
            }
            i += 1
        }
        if best < 0 { return nil }
        return tickets[best]
    }
    func assign(_ user: String) -> String {
        let t = nextOpen()
        if let ticket = t {
            ticket.status = .assigned
            ticket.assignee = user
            return ticket.label()
        }
        return "none"
    }
    func close(_ id: String) {
        for t in tickets { if t.id == id { t.status = .closed } }
    }
    func dump() { for t in tickets { print(t.label()) } }
}

let q = TicketQueue()
q.add(Ticket("T1", 2))
q.add(Ticket("T2", 5))
q.add(Ticket("T3", 3))
print(q.assign("alice"))
print(q.assign("bob"))
q.close("T2")
q.add(Ticket("T4", 8))
print(q.assign("carol"))
q.dump()
