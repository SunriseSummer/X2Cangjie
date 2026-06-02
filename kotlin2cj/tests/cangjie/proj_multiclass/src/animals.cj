package proj_multiclass

import std.collection.*

open class Animal {
    let name: String
    let legs: Int64
    init(name: String, legs: Int64) {
        this.name = name
        this.legs = legs
    }
    public open func speak(): String {
        return "${name} says nothing"
    }
    public open func describe(): String {
        return "${name} has ${legs} legs"
    }
}

class Dog <: Animal {
    init(name: String) {
        super(name, 4)
    }
    public override func speak(): String {
        return "${name} says Woof!"
    }
}

class Cat <: Animal {
    init(name: String) {
        super(name, 4)
    }
    public override func speak(): String {
        return "${name} says Meow!"
    }
}

class Bird <: Animal {
    init(name: String) {
        super(name, 2)
    }
    public override func speak(): String {
        return "${name} says Tweet!"
    }
    func canFly(): Bool {
        return true
    }
}

class Fish <: Animal {
    init(name: String) {
        super(name, 0)
    }
    public override func speak(): String {
        return "${name} says Blub!"
    }
    func canSwim(): Bool {
        return true
    }
}
