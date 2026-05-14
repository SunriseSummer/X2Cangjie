// Medium #2 (iter9): command router with prefix matching
class Handler {
    let prefix: String
    let name: String
    init(_ prefix: String, _ name: String) {
        self.prefix = prefix
        self.name = name
    }
    func matches(_ path: String) -> Bool {
        return path.hasPrefix(prefix)
    }
}

class Router {
    var handlers: [Handler] = []
    func add(_ prefix: String, _ name: String) {
        handlers.append(Handler(prefix, name))
    }
    func route(_ path: String) -> String {
        var best = "not_found"
        var bestLen = -1
        for h in handlers {
            if h.matches(path) && h.prefix.count > bestLen {
                best = h.name
                bestLen = h.prefix.count
            }
        }
        return best
    }
}

let r = Router()
r.add("/", "root")
r.add("/api", "api")
r.add("/api/users", "users")
r.add("/static", "static")
for p in ["/", "/api", "/api/users/42", "/api/orders", "/static/app.js", "/x"] {
    print("\(p) -> \(r.route(p))")
}
