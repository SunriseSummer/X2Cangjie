interface Animal {
    func Sound(): String
    func Name(): String
}

open class Dog <: Animal {
    public var name: String
    public init(name: String) {
        this.name = name
    }
    public override func Sound(): String { return "Woof" }
    public override func Name(): String { return this.name }
}

open class Cat <: Animal {
    public var name: String
    public init(name: String) {
        this.name = name
    }
    public override func Sound(): String { return "Meow" }
    public override func Name(): String { return this.name }
}

func describe(a: Animal): Unit {
    println(a.Name() + " says " + a.Sound())
}

main() {
    describe(Dog("Rex"))
    describe(Cat("Whiskers"))
    return 0
}
