import std.collection.*

open class Animal <: ToString {
    let name: String
    let sound: String
    init(name: String, sound: String) {
        this.name = name
        this.sound = sound
    }
    public open func speak(): String {
        return "${name} says ${sound}"
    }
    public open func `type`(): String {
        return "Animal"
    }
    public open override func toString(): String {
        return "${`type`()}: ${speak()}"
    }
}

open class Pet <: Animal {
    let owner: String
    init(name: String, sound: String, owner: String) {
        super(name, sound)
        this.owner = owner
    }
    public open override func `type`(): String {
        return "Pet"
    }
    public open func greetOwner(): String {
        return "${name} greets ${owner}"
    }
}

class Dog <: Pet {
    init(name: String, owner: String) {
        super(name, "Woof", owner)
    }
    public override func `type`(): String {
        return "Dog"
    }
    func fetch(): String {
        return "${name} fetches the ball"
    }
}

class Cat <: Pet {
    init(name: String, owner: String) {
        super(name, "Meow", owner)
    }
    public override func `type`(): String {
        return "Cat"
    }
    func purr(): String {
        return "${name} purrs"
    }
}

main() {
    let animals = ArrayList<Animal>()
    let dog = Dog("Rex", "Alice")
    let cat = Cat("Whiskers", "Bob")
    animals.add(dog)
    animals.add(cat)
    animals.add(Animal("Parrot", "Squawk"))
    for (a in animals) {
        println(a)
    }
    println(dog.greetOwner())
    println(dog.fetch())
    println(cat.greetOwner())
    println(cat.purr())
    for (a in animals) {
        match (a) {
            case a: Dog => println("${a.name} is a dog owned by ${a.owner}")
            case a: Cat => println("${a.name} is a cat owned by ${a.owner}")
            case _ => println("${a.name} is a generic animal")}
    }
}
