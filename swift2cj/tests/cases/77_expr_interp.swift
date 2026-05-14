// Large #1: expression interpreter (~200 lines) — recursive enum, dispatch via switch
indirect enum Expr {
    case num(Int)
    case neg(Expr)
    case add(Expr, Expr)
    case sub(Expr, Expr)
    case mul(Expr, Expr)
    case div(Expr, Expr)
    case ifz(Expr, Expr, Expr)   // if expr1 == 0 then expr2 else expr3
}

func eval(_ e: Expr) -> Int {
    switch e {
    case .num(let n):
        return n
    case .neg(let x):
        return -eval(x)
    case .add(let a, let b):
        return eval(a) + eval(b)
    case .sub(let a, let b):
        return eval(a) - eval(b)
    case .mul(let a, let b):
        return eval(a) * eval(b)
    case .div(let a, let b):
        return eval(a) / eval(b)
    case .ifz(let c, let t, let f):
        if eval(c) == 0 {
            return eval(t)
        } else {
            return eval(f)
        }
    }
}

func render(_ e: Expr) -> String {
    switch e {
    case .num(let n):
        return "\(n)"
    case .neg(let x):
        return "(- " + render(x) + ")"
    case .add(let a, let b):
        return "(+ " + render(a) + " " + render(b) + ")"
    case .sub(let a, let b):
        return "(- " + render(a) + " " + render(b) + ")"
    case .mul(let a, let b):
        return "(* " + render(a) + " " + render(b) + ")"
    case .div(let a, let b):
        return "(/ " + render(a) + " " + render(b) + ")"
    case .ifz(let c, let t, let f):
        return "(ifz " + render(c) + " " + render(t) + " " + render(f) + ")"
    }
}

func depth(_ e: Expr) -> Int {
    switch e {
    case .num(_):
        return 1
    case .neg(let x):
        return 1 + depth(x)
    case .add(let a, let b):
        let da = depth(a)
        let db = depth(b)
        return 1 + ((da > db) ? da : db)
    case .sub(let a, let b):
        let da = depth(a)
        let db = depth(b)
        return 1 + ((da > db) ? da : db)
    case .mul(let a, let b):
        let da = depth(a)
        let db = depth(b)
        return 1 + ((da > db) ? da : db)
    case .div(let a, let b):
        let da = depth(a)
        let db = depth(b)
        return 1 + ((da > db) ? da : db)
    case .ifz(let c, let t, let f):
        let dc = depth(c)
        let dt = depth(t)
        let df = depth(f)
        var m = dc
        if dt > m { m = dt }
        if df > m { m = df }
        return 1 + m
    }
}

// Build some expressions
let e1: Expr = .add(.num(3), .num(4))
let e2: Expr = .mul(.add(.num(2), .num(3)), .sub(.num(10), .num(4)))
let e3: Expr = .neg(.div(.num(20), .num(4)))
let e4: Expr = .ifz(.sub(.num(7), .num(7)), .num(99), .num(0))
let e5: Expr = .add(.mul(.num(6), .num(7)), .neg(.add(.num(1), .num(2))))

let all: [Expr] = [e1, e2, e3, e4, e5]
var idx = 0
for e in all {
    idx += 1
    print("e\(idx): " + render(e) + " = \(eval(e)) [depth=\(depth(e))]")
}

// Build a deeper tree programmatically
var deep: Expr = .num(1)
var i = 2
while i <= 6 {
    deep = .add(deep, .num(i))
    i += 1
}
print("deep: " + render(deep) + " = \(eval(deep)) [depth=\(depth(deep))]")

// Simulate a small "program"
let prog: Expr = .ifz(
    .sub(.num(5), .num(5)),
    .mul(.num(10), .add(.num(2), .num(3))),
    .num(-1)
)
print("prog = \(eval(prog))")
print("render = " + render(prog))
print("depth  = \(depth(prog))")
