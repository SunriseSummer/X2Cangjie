interface Animal {
    func Sound(): String
    func Name(): String
}

open class Dog <: Animal {
    public var name: String
    public init(name: String) {
        this.name = name
    }
    public func Sound(): String {
        return "woof"
    }
    public func Name(): String {
        return this.name
    }
}

func describe(a: Animal): Unit {
    println("${a.Name()} ${a.Sound()}")
}

main() {
    describe(Dog("Rex"))
    return 0
}
