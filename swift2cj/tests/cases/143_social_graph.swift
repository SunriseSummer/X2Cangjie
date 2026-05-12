// Large #1 (iter11): social graph mutual friends and distance
class SocialGraph {
    var edges: [String: [String]] = [:]
    func add(_ a: String, _ b: String) {
        var ax = edges[a] ?? []
        ax.append(b)
        edges[a] = ax
        var bx = edges[b] ?? []
        bx.append(a)
        edges[b] = bx
    }
    func mutual(_ a: String, _ b: String) -> [String] {
        let ax = edges[a] ?? []
        let bx = edges[b] ?? []
        var out: [String] = []
        for x in ax {
            for y in bx { if x == y { out.append(x) } }
        }
        return sortStrings(out)
    }
    func distance(_ start: String, _ goal: String) -> Int {
        var q: [String] = []
        var dist: [String: Int] = [:]
        q.append(start)
        dist[start] = 0
        var head = 0
        while head < q.count {
            let cur = q[head]
            head += 1
            if cur == goal { return dist[cur] ?? 0 }
            let ns = edges[cur] ?? []
            for n in ns {
                if dist[n] == nil {
                    dist[n] = (dist[cur] ?? 0) + 1
                    q.append(n)
                }
            }
        }
        return -1
    }
}

func sortStrings(_ xs: [String]) -> [String] {
    var out = xs
    var i = 1
    while i < out.count {
        var j = i
        while j > 0 && out[j] < out[j - 1] {
            let t = out[j]
            out[j] = out[j - 1]
            out[j - 1] = t
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

let sg = SocialGraph()
sg.add("alice", "bob")
sg.add("alice", "carol")
sg.add("bob", "dave")
sg.add("carol", "dave")
sg.add("dave", "erin")
print("mutual alice/dave=" + join(sg.mutual("alice", "dave")))
print("dist alice/erin=\(sg.distance("alice", "erin"))")
print("dist bob/carol=\(sg.distance("bob", "carol"))")
