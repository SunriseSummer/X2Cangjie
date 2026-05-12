// Small #1 (iter5): closure factory via class wrapper (Cangjie-friendly)
class Counter {
    var n: Int
    init(_ start: Int) {
        self.n = start
    }
    func next() -> Int {
        n += 1
        return n
    }
}

class Stepper {
    var n: Int
    var step: Int
    init(_ start: Int, _ step: Int) {
        self.n = start
        self.step = step
    }
    func tick() -> Int {
        let r = n
        n += step
        return r
    }
}

let c1 = Counter(0)
print(c1.next())
print(c1.next())
print(c1.next())

let c2 = Counter(100)
print(c2.next())
print(c2.next())
print(c1.next())   // independent state
print(c2.next())

let s = Stepper(0, 3)
var i = 0
var collected: [Int] = []
while i < 5 {
    collected.append(s.tick())
    i += 1
}
print("stepper: \(collected)")

