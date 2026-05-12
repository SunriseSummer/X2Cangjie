// Medium #2 (iter7): simple event rule engine with enum actions
enum Action {
    case allow
    case deny
    case score(Int)
}

class Event {
    let user: String
    let kind: String
    let amount: Int
    init(_ user: String, _ kind: String, _ amount: Int) {
        self.user = user
        self.kind = kind
        self.amount = amount
    }
}

class Rule {
    let kind: String
    let limit: Int
    let action: Action
    init(_ kind: String, _ limit: Int, _ action: Action) {
        self.kind = kind
        self.limit = limit
        self.action = action
    }

    func apply(_ e: Event) -> Action? {
        if e.kind == kind && e.amount >= limit {
            return action
        }
        return nil
    }
}

func actionName(_ a: Action) -> String {
    switch a {
    case .allow:
        return "allow"
    case .deny:
        return "deny"
    case .score(let n):
        return "score(\(n))"
    }
}

class Engine {
    var rules: [Rule] = []
    func add(_ r: Rule) {
        rules.append(r)
    }
    func decide(_ e: Event) -> Action {
        var score = 0
        for r in rules {
            let a = r.apply(e)
            if let aa = a {
                switch aa {
                case .deny:
                    return .deny
                case .allow:
                    return .allow
                case .score(let n):
                    score += n
                }
            }
        }
        if score >= 10 {
            return .deny
        }
        return .allow
    }
}

let engine = Engine()
engine.add(Rule("login", 5, .score(3)))
engine.add(Rule("purchase", 100, .score(7)))
engine.add(Rule("purchase", 500, .deny))
engine.add(Rule("profile", 1, .allow))
let events = [
    Event("alice", "login", 7),
    Event("bob", "purchase", 120),
    Event("carol", "purchase", 900),
    Event("dave", "profile", 1),
    Event("eve", "unknown", 0)
]
for e in events {
    print("\(e.user)/\(e.kind)/\(e.amount) -> \(actionName(engine.decide(e)))")
}
