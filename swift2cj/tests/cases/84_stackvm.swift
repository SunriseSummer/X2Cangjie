// Large #2 (iter2): tiny stack VM with opcodes (~280 lines)
enum Op {
    case push(Int)
    case pop
    case add
    case sub
    case mul
    case dup
    case swap
    case jmp(Int)
    case jz(Int)
    case prn
    case halt
}

class VM {
    var stack: [Int] = []
    var pc: Int = 0
    var halted: Bool = false
    var trace: [String] = []
    var prints: [Int] = []
    let program: [Op]

    init(_ program: [Op]) {
        self.program = program
    }

    func push(_ v: Int) {
        stack.append(v)
    }

    func pop() -> Int {
        let n = stack.count
        let v = stack[n - 1]
        stack.remove(at: n - 1)
        return v
    }

    func top() -> Int {
        let n = stack.count
        return stack[n - 1]
    }

    func step() {
        if halted {
            return
        }
        let op = program[pc]
        switch op {
        case .push(let v):
            push(v)
            trace.append("push \(v)")
            pc += 1
        case .pop:
            let _ = pop()
            trace.append("pop")
            pc += 1
        case .add:
            let b = pop()
            let a = pop()
            push(a + b)
            trace.append("add")
            pc += 1
        case .sub:
            let b = pop()
            let a = pop()
            push(a - b)
            trace.append("sub")
            pc += 1
        case .mul:
            let b = pop()
            let a = pop()
            push(a * b)
            trace.append("mul")
            pc += 1
        case .dup:
            push(top())
            trace.append("dup")
            pc += 1
        case .swap:
            let b = pop()
            let a = pop()
            push(b)
            push(a)
            trace.append("swap")
            pc += 1
        case .jmp(let t):
            trace.append("jmp \(t)")
            pc = t
        case .jz(let t):
            let v = pop()
            trace.append("jz \(t) (popped \(v))")
            if v == 0 {
                pc = t
            } else {
                pc += 1
            }
        case .prn:
            let v = top()
            prints.append(v)
            trace.append("prn \(v)")
            pc += 1
        case .halt:
            trace.append("halt")
            halted = true
        }
    }

    func runFor(_ steps: Int) {
        var i = 0
        while i < steps && !halted {
            step()
            i += 1
        }
    }

    func stackDump() -> String {
        var s = "stack=["
        var first = true
        for v in stack {
            if !first {
                s = s + ","
            }
            s = s + "\(v)"
            first = false
        }
        s = s + "]"
        return s
    }
}

func runProgram(_ ops: [Op], maxSteps: Int) -> VM {
    let vm = VM(ops)
    vm.runFor(maxSteps)
    return vm
}

// Program 1: compute (3 + 4) * 2 and print
let p1: [Op] = [
    .push(3), .push(4), .add,
    .push(2), .mul,
    .prn, .halt
]
let vm1 = runProgram(p1, maxSteps: 20)
print("p1 prints = \(vm1.prints)")
print("p1 final \(vm1.stackDump())")
print("p1 trace size = \(vm1.trace.count)")

// Program 2: dup / swap
let p2: [Op] = [
    .push(10), .dup, .add,    // 20
    .push(5), .swap, .sub,    // 5 - 20 = -15
    .prn, .halt
]
let vm2 = runProgram(p2, maxSteps: 30)
print("p2 prints = \(vm2.prints)")
print("p2 final \(vm2.stackDump())")

// Program 3: loop that prints 5,4,3,2,1
// pseudo:
//  push 5
// loop:
//  dup
//  prn
//  push 1
//  sub
//  dup
//  jz end       (if 0, jump to end)
//  jmp loop
// end:
//  pop
//  halt
let p3: [Op] = [
    /*0*/ .push(5),
    /*1*/ .dup,
    /*2*/ .prn,
    /*3*/ .push(1),
    /*4*/ .sub,
    /*5*/ .dup,
    /*6*/ .jz(9),
    /*7*/ .pop,
    /*8*/ .jmp(1),
    /*9*/ .pop,
    /*10*/ .halt
]
let vm3 = runProgram(p3, maxSteps: 200)
print("p3 prints = \(vm3.prints)")
print("p3 trace size = \(vm3.trace.count)")
print("p3 halted = \(vm3.halted)")

// Program 4: nothing - just halt
let p4: [Op] = [.halt]
let vm4 = runProgram(p4, maxSteps: 5)
print("p4 halted = \(vm4.halted) stack=\(vm4.stack.count)")
