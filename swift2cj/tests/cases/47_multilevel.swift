class A {
    func name() -> String {
        return "A"
    }
}
class B: A {
    override func name() -> String {
        return "B"
    }
}
class C: B {
    override func name() -> String {
        return "C"
    }
}
let xs: [A] = [A(), B(), C()]
for o in xs {
    print(o.name())
}
