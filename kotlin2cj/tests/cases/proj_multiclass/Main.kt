fun main() {
    val zoo = Zoo("City Zoo")

    zoo.addAnimal(Dog("Rex"))
    zoo.addAnimal(Cat("Whiskers"))
    zoo.addAnimal(Bird("Tweety"))
    zoo.addAnimal(Fish("Nemo"))
    zoo.addAnimal(Dog("Buddy"))

    zoo.rollCall()

    println("Total animals: ${zoo.totalAnimals()}")

    val counts = zoo.countByLegs()
    val keys = mutableListOf<Int>()
    for ((k, _) in counts) {
        keys.add(k)
    }
    // sort keys manually
    for (i in 0 until keys.size) {
        for (j in i + 1 until keys.size) {
            if (keys[j] < keys[i]) {
                val tmp = keys[i]
                keys[i] = keys[j]
                keys[j] = tmp
            }
        }
    }
    for (k in keys) {
        println("$k legs: ${counts[k]} animals")
    }

    for (animal in zoo.animals) {
        println(animal.describe())
    }
}
