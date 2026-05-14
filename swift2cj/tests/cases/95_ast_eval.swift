// Large #1 (iter4): integer-arithmetic AST interpreter with variables (~220 lines)
indirect enum AST {
    case num(Int)
    case variable(String)
    case neg(AST)
    case add(AST, AST)
    case sub(AST, AST)
    case mul(AST, AST)
    case div(AST, AST)
    case mod(AST, AST)
    case ifz(AST, AST, AST)   // if-zero: cond, then, else
}

class Env2 {
    var bindings: [String: Int] = [:]
    var trace: [String] = []
    func set(_ name: String, _ v: Int) {
        bindings[name] = v
    }
    func get(_ name: String) -> Int {
        return bindings[name] ?? 0
    }
}

func evalA(_ e: AST, _ env: Env2) -> Int {
    switch e {
    case .num(let n):
        return n
    case .variable(let s):
        let v = env.get(s)
        env.trace.append("get \(s) = \(v)")
        return v
    case .neg(let x):
        return -evalA(x, env)
    case .add(let a, let b):
        return evalA(a, env) + evalA(b, env)
    case .sub(let a, let b):
        return evalA(a, env) - evalA(b, env)
    case .mul(let a, let b):
        return evalA(a, env) * evalA(b, env)
    case .div(let a, let b):
        let bv = evalA(b, env)
        if bv == 0 {
            env.trace.append("div0")
            return 0
        }
        return evalA(a, env) / bv
    case .mod(let a, let b):
        let bv = evalA(b, env)
        if bv == 0 {
            env.trace.append("mod0")
            return 0
        }
        return evalA(a, env) % bv
    case .ifz(let cond, let thn, let els):
        let c = evalA(cond, env)
        if c == 0 {
            return evalA(thn, env)
        }
        return evalA(els, env)
    }
}

func showA(_ e: AST) -> String {
    switch e {
    case .num(let n):
        return "\(n)"
    case .variable(let s):
        return s
    case .neg(let x):
        return "(-" + showA(x) + ")"
    case .add(let a, let b):
        return "(" + showA(a) + " + " + showA(b) + ")"
    case .sub(let a, let b):
        return "(" + showA(a) + " - " + showA(b) + ")"
    case .mul(let a, let b):
        return "(" + showA(a) + " * " + showA(b) + ")"
    case .div(let a, let b):
        return "(" + showA(a) + " / " + showA(b) + ")"
    case .mod(let a, let b):
        return "(" + showA(a) + " % " + showA(b) + ")"
    case .ifz(let c, let t, let f):
        return "ifz(" + showA(c) + " ? " + showA(t) + " : " + showA(f) + ")"
    }
}

func countNodes(_ e: AST) -> Int {
    switch e {
    case .num:
        return 1
    case .variable:
        return 1
    case .neg(let x):
        return 1 + countNodes(x)
    case .add(let a, let b):
        return 1 + countNodes(a) + countNodes(b)
    case .sub(let a, let b):
        return 1 + countNodes(a) + countNodes(b)
    case .mul(let a, let b):
        return 1 + countNodes(a) + countNodes(b)
    case .div(let a, let b):
        return 1 + countNodes(a) + countNodes(b)
    case .mod(let a, let b):
        return 1 + countNodes(a) + countNodes(b)
    case .ifz(let c, let t, let f):
        return 1 + countNodes(c) + countNodes(t) + countNodes(f)
    }
}

// expr: (x + 3) * (y - 2)
let e1: AST = .mul(
    .add(.variable("x"), .num(3)),
    .sub(.variable("y"), .num(2))
)
print("e1 = " + showA(e1))
print("nodes = \(countNodes(e1))")

let env = Env2()
env.set("x", 5)
env.set("y", 10)
print("e1 with x=5, y=10 -> \(evalA(e1, env))")

// expr2: -(x * (y / 2 + 1))
let e2: AST = .neg(.mul(.variable("x"), .add(.div(.variable("y"), .num(2)), .num(1))))
print("e2 = " + showA(e2))
print("e2 -> \(evalA(e2, env))")
print("trace len after e2 = \(env.trace.count)")

// ifz: if (x - 5) == 0 then 100 else 200
let e3: AST = .ifz(.sub(.variable("x"), .num(5)), .num(100), .num(200))
print("e3 = " + showA(e3))
print("e3 (x=5) -> \(evalA(e3, env))")
env.set("x", 6)
print("e3 (x=6) -> \(evalA(e3, env))")

// div by zero
let e4: AST = .div(.num(10), .sub(.variable("y"), .variable("y")))
print("e4 = " + showA(e4))
print("e4 -> \(evalA(e4, env))")
print("trace contains div0? \(env.trace.count > 0)")

// undefined variable defaults to 0
let env2 = Env2()
let e5: AST = .add(.variable("z"), .num(42))
print("e5 with empty env -> \(evalA(e5, env2))")
