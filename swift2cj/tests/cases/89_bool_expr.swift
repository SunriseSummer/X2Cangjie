// Large #1 (iter3): mini boolean expression evaluator (parser by recursion) ~200 lines
indirect enum BExpr {
    case lit(Bool)
    case variable(String)
    case not(BExpr)
    case and(BExpr, BExpr)
    case or(BExpr, BExpr)
}

class Env {
    var bindings: [String: Bool] = [:]
    func set(_ name: String, _ v: Bool) {
        bindings[name] = v
    }
    func get(_ name: String) -> Bool {
        return bindings[name] ?? false
    }
}

func evalB(_ e: BExpr, _ env: Env) -> Bool {
    switch e {
    case .lit(let b):
        return b
    case .variable(let n):
        return env.get(n)
    case .not(let x):
        return !evalB(x, env)
    case .and(let a, let b):
        return evalB(a, env) && evalB(b, env)
    case .or(let a, let b):
        return evalB(a, env) || evalB(b, env)
    }
}

func showB(_ e: BExpr) -> String {
    switch e {
    case .lit(let b):
        if b { return "T" } else { return "F" }
    case .variable(let n):
        return n
    case .not(let x):
        return "!" + showB(x)
    case .and(let a, let b):
        return "(" + showB(a) + " & " + showB(b) + ")"
    case .or(let a, let b):
        return "(" + showB(a) + " | " + showB(b) + ")"
    }
}

// Simplify rules:
//   - x | !x => T
//   - x & !x => F
//   - !!x  => x
//   - x & T => x ; x & F => F
//   - x | F => x ; x | T => T
func simplify(_ e: BExpr) -> BExpr {
    switch e {
    case .lit(let b):
        return .lit(b)
    case .variable(let n):
        return .variable(n)
    case .not(let inner):
        let si = simplify(inner)
        switch si {
        case .not(let x2):
            return x2
        case .lit(let b):
            return .lit(!b)
        default:
            return .not(si)
        }
    case .and(let a, let b):
        let sa = simplify(a)
        let sb = simplify(b)
        switch sa {
        case .lit(let v):
            if v { return sb } else { return .lit(false) }
        default:
            break
        }
        switch sb {
        case .lit(let v):
            if v { return sa } else { return .lit(false) }
        default:
            break
        }
        return .and(sa, sb)
    case .or(let a, let b):
        let sa = simplify(a)
        let sb = simplify(b)
        switch sa {
        case .lit(let v):
            if v { return .lit(true) } else { return sb }
        default:
            break
        }
        switch sb {
        case .lit(let v):
            if v { return .lit(true) } else { return sa }
        default:
            break
        }
        return .or(sa, sb)
    }
}

// (a & b) | (!a & !b)  — XNOR
let e1: BExpr = .or(
    .and(.variable("a"), .variable("b")),
    .and(.not(.variable("a")), .not(.variable("b")))
)
print("expr1 = " + showB(e1))

let env = Env()
env.set("a", true)
env.set("b", true)
print("a=T b=T -> \(evalB(e1, env))")
env.set("b", false)
print("a=T b=F -> \(evalB(e1, env))")
env.set("a", false)
env.set("b", false)
print("a=F b=F -> \(evalB(e1, env))")

// double-negation
let e2: BExpr = .not(.not(.variable("x")))
print("expr2 = " + showB(e2))
print("simplified = " + showB(simplify(e2)))

// simplification with literals
let e3: BExpr = .and(.variable("a"), .lit(true))
print("expr3 simplified = " + showB(simplify(e3)))

let e4: BExpr = .or(.lit(false), .and(.lit(true), .variable("b")))
print("expr4 simplified = " + showB(simplify(e4)))

let e5: BExpr = .and(.variable("a"), .lit(false))
print("expr5 simplified = " + showB(simplify(e5)))

// big OR over 5 variables
let names = ["a", "b", "c", "d", "e"]
var big: BExpr = .lit(false)
for n in names {
    big = .or(big, .variable(n))
}
print("big = " + showB(big))
print("big simplified = " + showB(simplify(big)))
let envBig = Env()
envBig.set("c", true)
print("big with c=T -> \(evalB(big, envBig))")
let envEmpty = Env()
print("big with nothing -> \(evalB(big, envEmpty))")
