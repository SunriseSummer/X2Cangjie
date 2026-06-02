package proj_multiclass

import std.collection.*

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
