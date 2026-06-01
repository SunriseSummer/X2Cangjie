class Zoo(val zooName: String) {
    val animals = mutableListOf<Animal>()

    fun addAnimal(animal: Animal) {
        animals.add(animal)
        println("Added ${animal.name} to $zooName")
    }

    fun rollCall() {
        println("--- Roll Call at $zooName ---")
        for (animal in animals) {
            println("  ${animal.speak()}")
        }
    }

    fun countByLegs(): HashMap<Int, Int> {
        val counts = HashMap<Int, Int>()
        for (animal in animals) {
            counts[animal.legs] = (counts[animal.legs] ?: 0) + 1
        }
        return counts
    }

    fun totalAnimals(): Int = animals.size
}
