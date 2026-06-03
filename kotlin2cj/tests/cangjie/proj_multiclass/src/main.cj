package proj_multiclass

import std.collection.*

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
