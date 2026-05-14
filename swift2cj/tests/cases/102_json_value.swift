// Large #2 (iter5): JSON-like value model with formatter (~250 lines)
indirect enum JV {
    case null
    case bool(Bool)
    case int(Int)
    case str(String)
    case arr([JV])
    case obj([String: JV])
}

func jsonOf(_ v: JV) -> String {
    switch v {
    case .null:
        return "null"
    case .bool(let b):
        if b { return "true" } else { return "false" }
    case .int(let n):
        return "\(n)"
    case .str(let s):
        return "\"" + s + "\""
    case .arr(let xs):
        var s = "["
        var first = true
        for x in xs {
            if !first {
                s = s + ","
            }
            s = s + jsonOf(x)
            first = false
        }
        return s + "]"
    case .obj(let kv):
        var s = "{"
        var first = true
        // deterministic key order: collect & sort by string
        var keys: [String] = []
        for (k, _) in kv {
            keys.append(k)
        }
        // simple insertion sort
        var i = 1
        while i < keys.count {
            var j = i
            while j > 0 && keys[j] < keys[j - 1] {
                let tmp = keys[j]
                keys[j] = keys[j - 1]
                keys[j - 1] = tmp
                j -= 1
            }
            i += 1
        }
        for k in keys {
            if !first {
                s = s + ","
            }
            s = s + "\"" + k + "\":"
            s = s + jsonOf(kv[k] ?? JV.null)
            first = false
        }
        return s + "}"
    }
}

func depth(_ v: JV) -> Int {
    switch v {
    case .null:
        return 1
    case .bool:
        return 1
    case .int:
        return 1
    case .str:
        return 1
    case .arr(let xs):
        var d = 0
        for x in xs {
            let dd = depth(x)
            if dd > d { d = dd }
        }
        return d + 1
    case .obj(let kv):
        var d = 0
        for (_, v) in kv {
            let dd = depth(v)
            if dd > d { d = dd }
        }
        return d + 1
    }
}

func countNodes(_ v: JV) -> Int {
    switch v {
    case .null: return 1
    case .bool: return 1
    case .int: return 1
    case .str: return 1
    case .arr(let xs):
        var c = 1
        for x in xs {
            c += countNodes(x)
        }
        return c
    case .obj(let kv):
        var c = 1
        for (_, v) in kv {
            c += countNodes(v)
        }
        return c
    }
}

// Build sample objects.
let a: JV = .arr([.int(1), .int(2), .int(3)])
print("a = " + jsonOf(a))
print("a depth = \(depth(a))  nodes = \(countNodes(a))")

let b: JV = .obj([
    "id": .int(42),
    "name": .str("widget"),
    "active": .bool(true),
    "tags": .arr([.str("red"), .str("blue")])
])
print("b = " + jsonOf(b))
print("b depth = \(depth(b))")
print("b nodes = \(countNodes(b))")

let nested: JV = .obj([
    "user": .obj([
        "name": .str("alice"),
        "scores": .arr([.int(80), .int(95), .int(70)])
    ]),
    "ok": .bool(true),
    "errors": .arr([])
])
print("nested = " + jsonOf(nested))
print("nested depth = \(depth(nested))")
print("nested nodes = \(countNodes(nested))")

let mix: JV = .arr([
    .obj(["k": .int(1)]),
    .obj(["k": .int(2)]),
    .null,
    .str("end")
])
print("mix = " + jsonOf(mix))
print("mix depth = \(depth(mix))")
print("mix nodes = \(countNodes(mix))")
