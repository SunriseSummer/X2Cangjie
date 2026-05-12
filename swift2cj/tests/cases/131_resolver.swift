// Large #1 (iter9): package dependency resolver with missing dependency report
class Package {
    let name: String
    var deps: [String] = []
    init(_ name: String) { self.name = name }
    func dep(_ name: String) { deps.append(name) }
}

class Resolver {
    var packages: [String: Package] = [:]
    func add(_ p: Package) { packages[p.name] = p }
    func exists(_ name: String) -> Bool { return packages[name] != nil }
    func missing() -> [String] {
        var out: [String] = []
        for (_, p) in packages {
            for d in p.deps {
                if !exists(d) {
                    var seen = false
                    for x in out { if x == d { seen = true } }
                    if !seen { out.append(d) }
                }
            }
        }
        return sortStrings(out)
    }
    func installOrder(_ root: String) -> [String] {
        var seen: [String: Bool] = [:]
        var out: [String] = []
        visit(root, &seen, &out)
        return out
    }
    func visit(_ name: String, _ seen: inout [String: Bool], _ out: inout [String]) {
        if seen[name] ?? false { return }
        seen[name] = true
        let p = packages[name]
        if let pp = p {
            for d in pp.deps { visit(d, &seen, &out) }
            out.append(name)
        }
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

let core = Package("core")
let net = Package("net")
net.dep("core")
let web = Package("web")
web.dep("net")
web.dep("json")
let app = Package("app")
app.dep("web")
app.dep("db")
let resolver = Resolver()
resolver.add(core)
resolver.add(net)
resolver.add(web)
resolver.add(app)

func joinStrings(_ xs: [String]) -> String {
    var s = ""
    var i = 0
    while i < xs.count {
        if i > 0 { s = s + "," }
        s = s + xs[i]
        i += 1
    }
    return s
}

print("missing=" + joinStrings(resolver.missing()))
print("order=" + joinStrings(resolver.installOrder("app")))
