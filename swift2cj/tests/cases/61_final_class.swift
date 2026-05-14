// final class
final class Counter {
    var n: Int = 0
    func inc() { self.n += 1 }
    func get() -> Int { return self.n }
}
let c = Counter()
c.inc()
c.inc()
c.inc()
print(c.get())
