open class Animal {
    var name: String = ""
    init(name: String) {
        this.name = name
    }
    public open func speak(): String {
        return "generic sound"
    }
}

open class Dog <: Animal {
    init(name: String) {
        super(name)
    }
    public override func speak(): String {
        return "woof"
    }
}

let a = Animal("X")

let d = Dog("Rex")

main() {
    println(a.speak())
    println(d.speak())
    return 0
}
