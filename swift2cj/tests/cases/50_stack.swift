class Stack {
    var data: [Int] = []
    func push(_ x: Int) {
        self.data.append(x)
    }
    func top() -> Int {
        return self.data[self.data.count - 1]
    }
    func size() -> Int {
        return self.data.count
    }
}
let s = Stack()
s.push(1)
s.push(2)
s.push(3)
print(s.size())
print(s.top())
s.push(99)
print(s.top())
print(s.size())
