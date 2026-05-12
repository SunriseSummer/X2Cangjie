class Stats {
    var data: [Int] = []
    func add(_ x: Int) {
        self.data.append(x)
    }
    func sum() -> Int {
        var s: Int = 0
        for v in self.data {
            s = s + v
        }
        return s
    }
    func mean() -> Int {
        return self.sum() / self.data.count
    }
}
let s = Stats()
s.add(10)
s.add(20)
s.add(30)
s.add(40)
s.add(50)
print(s.sum())
print(s.mean())
