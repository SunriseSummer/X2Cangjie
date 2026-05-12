class Acc {
    var v: Int = 0
    func add(_ x: Int) -> Acc {
        self.v = self.v + x
        return self
    }
    func mul(_ x: Int) -> Acc {
        self.v = self.v * x
        return self
    }
    func get() -> Int {
        return self.v
    }
}
let a = Acc()
print(a.add(3).mul(4).add(2).get())
