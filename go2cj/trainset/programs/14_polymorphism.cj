import std.collection.*

interface Animal {
    func Sound(): String
}

open class Dog <: Animal {
    public var name: String
    public init(name: String) {
        this.name = name
    }
    public override func Sound(): String {
        return "woof"
    }
}

open class Cat <: Animal {
    public var name: String
    public init(name: String) {
        this.name = name
    }
    public override func Sound(): String {
        return "meow"
    }
}

main() {
    var xs = ArrayList<Animal>([Dog("rex"), Cat("tom"), Dog("buddy")])
    for (a in xs) {
        println(a.Sound())
    }
    return 0
}
