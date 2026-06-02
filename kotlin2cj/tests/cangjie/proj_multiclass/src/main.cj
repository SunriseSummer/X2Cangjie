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

class Zoo {
    let zooName: String
    init(zooName: String) {
        this.zooName = zooName
    }
    let animals = ArrayList<Animal>()
    func addAnimal(animal: Animal) {
        animals.add(animal)
        println("Added ${animal.name} to ${zooName}")
    }
    func rollCall() {
        println("--- Roll Call at ${zooName} ---")
        for (animal in animals) {
            println("  ${animal.speak()}")
        }
    }
    func countByLegs(): HashMap<Int64, Int64> {
        let counts = HashMap<Int64, Int64>()
        for (animal in animals) {
            counts[animal.legs] = (counts.get(animal.legs) ?? 0) + 1
        }
        return counts
    }
    func totalAnimals(): Int64 {
        return animals.size
    }
}

main() {
    let zoo = Zoo("City Zoo")
    zoo.addAnimal(Dog("Rex"))
    zoo.addAnimal(Cat("Whiskers"))
    zoo.addAnimal(Bird("Tweety"))
    zoo.addAnimal(Fish("Nemo"))
    zoo.addAnimal(Dog("Buddy"))
    zoo.rollCall()
    println("Total animals: ${zoo.totalAnimals()}")
    let counts = zoo.countByLegs()
    let keys = ArrayList<Int64>()
    for ((k, _) in counts) {
        keys.add(k)
    }
    for (i in 0..keys.size) {
        for (j in (i + 1)..keys.size) {
            if (keys[j] < keys[i]) {
                let tmp = keys[i]
                keys[i] = keys[j]
                keys[j] = tmp
            }
        }
    }
    for (k in keys) {
        println("${k} legs: ${counts[k]} animals")
    }
    for (animal in zoo.animals) {
        println(animal.describe())
    }
}