enum Op {
    case add
    case sub
    case mul
}
func apply(_ o: Op, _ a: Int, _ b: Int) -> Int {
    switch o {
    case .add:
        return a + b
    case .sub:
        return a - b
    case .mul:
        return a * b
    }
}
print(apply(.add, 3, 4))
print(apply(.sub, 10, 3))
print(apply(.mul, 6, 7))
