// Medium #2 (iter3): RPN calculator over Int stack with pre-tokenised input (~100 lines)
class Step {
    let isOp: Bool
    let op: String
    let v: Int
    init(op: String) {
        self.isOp = true
        self.op = op
        self.v = 0
    }
    init(v: Int) {
        self.isOp = false
        self.op = ""
        self.v = v
    }
}

class RPN {
    var stack: [Int] = []
    var ops: [String] = []
    var error: String = ""

    func push(_ v: Int) {
        stack.append(v)
    }

    func pop() -> Int {
        let n = stack.count
        let v = stack[n - 1]
        stack.remove(at: n - 1)
        return v
    }

    func apply(_ op: String) {
        if stack.count < 2 {
            error = "stack underflow on \(op)"
            return
        }
        let b = pop()
        let a = pop()
        if op == "+" {
            push(a + b)
        } else if op == "-" {
            push(a - b)
        } else if op == "*" {
            push(a * b)
        } else if op == "/" {
            if b == 0 {
                error = "div by zero"
                push(a)
                push(b)
                return
            }
            push(a / b)
        } else if op == "%" {
            if b == 0 {
                error = "mod by zero"
                push(a)
                push(b)
                return
            }
            push(a % b)
        } else {
            error = "unknown op \(op)"
            push(a)
            push(b)
        }
        ops.append(op)
    }

    func feed(_ steps: [Step]) {
        for s in steps {
            if s.isOp {
                apply(s.op)
                if error != "" {
                    return
                }
            } else {
                push(s.v)
            }
        }
    }

    func result() -> Int {
        return stack[stack.count - 1]
    }
}

let c1 = RPN()
c1.feed([Step(v: 3), Step(v: 4), Step(op: "+")])
print("3 4 + = \(c1.result()) err='\(c1.error)' ops=\(c1.ops.count)")

let c2 = RPN()
c2.feed([Step(v: 10), Step(v: 5), Step(op: "-"), Step(v: 2), Step(op: "*")])
print("10 5 - 2 * = \(c2.result())")

let c3 = RPN()
c3.feed([Step(v: 100), Step(v: 7), Step(op: "/"), Step(v: 3), Step(op: "%")])
print("100 7 / 3 % = \(c3.result())")

let c4 = RPN()
c4.feed([Step(v: 1), Step(v: 2), Step(v: 3), Step(v: 4), Step(op: "+"), Step(op: "+"), Step(op: "+")])
print("1+2+3+4 = \(c4.result())")

// error: divide by zero
let c5 = RPN()
c5.feed([Step(v: 10), Step(v: 0), Step(op: "/")])
print("10 0 / err='\(c5.error)' top=\(c5.result())")

// error: stack underflow
let c6 = RPN()
c6.feed([Step(v: 5), Step(op: "+")])
print("5 + err='\(c6.error)'")

