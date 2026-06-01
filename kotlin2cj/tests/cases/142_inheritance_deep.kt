// Inheritance chain: 3-level deep with method overrides
open class Animal(val name: String, val sound: String) {
    open fun speak(): String = "$name says $sound"
    open fun type(): String = "Animal"
    override fun toString(): String = "${type()}: ${speak()}"
}

open class Pet(name: String, sound: String, val owner: String) : Animal(name, sound) {
    override fun type(): String = "Pet"
    fun greetOwner(): String = "$name greets $owner"
}

class Dog(name: String, owner: String) : Pet(name, "Woof", owner) {
    override fun type(): String = "Dog"
    fun fetch(): String = "$name fetches the ball"
}

class Cat(name: String, owner: String) : Pet(name, "Meow", owner) {
    override fun type(): String = "Cat"
    fun purr(): String = "$name purrs"
}

fun main() {
    val animals = ArrayList<Animal>()
    val dog = Dog("Rex", "Alice")
    val cat = Cat("Whiskers", "Bob")
    animals.add(dog)
    animals.add(cat)
    animals.add(Animal("Parrot", "Squawk"))

    for (a in animals) {
        println(a)
    }

    // Pet-specific operations
    println(dog.greetOwner())
    println(dog.fetch())
    println(cat.greetOwner())
    println(cat.purr())

    // Type checking
    for (a in animals) {
        when (a) {
            is Dog -> println("${a.name} is a dog owned by ${a.owner}")
            is Cat -> println("${a.name} is a cat owned by ${a.owner}")
            else -> println("${a.name} is a generic animal")
        }
    }
}
