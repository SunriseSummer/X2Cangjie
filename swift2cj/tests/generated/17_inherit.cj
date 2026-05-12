open class Animal {
    var name: String = ""
    public init(name: String) {
        this.name = name
    }
    public open func speak(): String {
        return "..."
    }
}

open class Dog <: Animal {
    public init(name: String) {
        super(name)
    }
    public override func speak(): String {
        return "woof"
    }
}

let a: Animal = Animal("a")

let d: Animal = Dog("rex")

main() {
    println(a.speak())
    println(d.speak())
    return 0
}
